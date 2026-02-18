from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from app.db.base import get_db
from app.models.sql import Transaction, Alert, SAR
from app.schemas.responses import Case, CaseList
from app.core.security import verify_api_key

router = APIRouter(dependencies=[verify_api_key])

@router.get("", response_model=CaseList)
async def list_cases(db: AsyncSession = Depends(get_db)):
    """
    List unique accounts (starting with 'IN-') with their risk status.
    Now includes cases with 0 alerts.
    """
    # 1. Get all unique accounts starting with 'IN-' from Transactions
    # Union of senders and receivers
    q1 = select(Transaction.sender_account).where(Transaction.sender_account.like("IN-%")).distinct()
    q2 = select(Transaction.receiver_account).where(Transaction.receiver_account.like("IN-%")).distinct()
    
    r1 = await db.execute(q1)
    r2 = await db.execute(q2)
    
    accounts = set(r1.scalars().all()) | set(r2.scalars().all())
    
    cases = []
    for acc_num in accounts:
        # 2. Count alerts for this account
        alert_query = select(func.count(Alert.alert_id)).where(Alert.account_number == acc_num)
        alert_res = await db.execute(alert_query)
        count = alert_res.scalar_one_or_none() or 0
        
        # 3. Get customer info from a transaction
        tx_query = select(Transaction).where(
            (Transaction.sender_account == acc_num) | (Transaction.receiver_account == acc_num)
        ).limit(1)
        tx_result = await db.execute(tx_query)
        tx = tx_result.scalar_one_or_none()
        
        # 4. Get Typology
        typ_query = select(Alert.rule_name).where(Alert.account_number == acc_num).limit(1)
        typ_result = await db.execute(typ_query)
        typology = typ_result.scalar_one_or_none() or "General Banking"

        # 5. Check for High Value Transactions (for Risk logic)
        hv_query = select(Transaction).where(
            ((Transaction.sender_account == acc_num) | (Transaction.receiver_account == acc_num)) & 
            (Transaction.amount > 100000)
        ).limit(1)
        hv_res = await db.execute(hv_query)
        has_hv = hv_res.scalar_one_or_none() is not None

        # Risk Logic
        risk_rating = "LOW"
        if count > 0: risk_rating = "MEDIUM"
        if count > 2 or has_hv: risk_rating = "HIGH"
        # Overwrite if count is 0 and no HV -> LOW
        
        # Refined Logic matched to user request
        if count == 0 and not has_hv:
            risk_rating = "LOW"
        elif count == 0 and has_hv:
            risk_rating = "MEDIUM" # High value but clean?
        elif count > 5:
            risk_rating = "HIGH"

        cases.append(Case(
            account_number=acc_num,
            customer_id=f"CUST-{acc_num.split('-')[-1]}",
            customer_name="Customer Name (DB Placeholder)" if not tx else (tx.description or "Retail Customer"),
            risk_rating=risk_rating,
            alert_count=count,
            typology=typology,
            status="PENDING"
        ))
        
    return CaseList(cases=cases)

@router.get("/history/submitted")
async def list_submitted_cases(db: AsyncSession = Depends(get_db)):
    """
    List all SARs that have been verified or finalized.
    """
    query = select(SAR).where(SAR.status.in_(["VERIFIED", "FINALIZED"])).order_by(SAR.generated_at.desc())
    result = await db.execute(query)
    sars = result.scalars().all()
    
    return [
        {
            "sar_id": s.sar_id,
            "account_number": s.customer_id.replace("CUST-", "") if s.customer_id else "Unknown",
            "submitted_at": s.generated_at,
            "officer_id": s.officer_id,
            "auditor_id": s.auditor_id,
            "status": s.status
        }
        for s in sars
    ]

@router.get("/history/{sar_id}")
async def get_submitted_report(sar_id: str, db: AsyncSession = Depends(get_db)):
    query = select(SAR).where(SAR.sar_id == sar_id)
    result = await db.execute(query)
    sar = result.scalar_one_or_none()
    
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
        
    return {
        "sar_id": sar.sar_id,
        "content": sar.edited_content or sar.content,
        "status": sar.status
    }

@router.get("/{account_number}")
async def get_case_details(account_number: str, db: AsyncSession = Depends(get_db)):
    """
    Get all transactions and alerts for a specific case with dynamic logic.
    """
    tx_query = select(Transaction).where(
        (Transaction.sender_account == account_number) | (Transaction.receiver_account == account_number)
    )
    al_query = select(Alert).where(Alert.account_number == account_number)
    
    tx_result = await db.execute(tx_query)
    al_result = await db.execute(al_query)
    
    transactions = []
    tx_objects = tx_result.scalars().all()
    
    # Anomaly Detection Logic
    amounts = [t.amount for t in tx_objects]
    if amounts:
        avg_amt = sum(amounts) / len(amounts)
        # Simplified Check: Is it > 2x Average OR > 100k?
        # A real system would use Std Dev, but this is sufficient for demo 
        # to show dynamic behavior vs hardcoded.
    else:
        avg_amt = 0

    for t in tx_objects:
        d = t.__dict__.copy()
        d.pop('_sa_instance_state', None)
        
        # Dynamic Anomaly Flag
        is_high_val = t.amount > 100000
        is_spike = (avg_amt > 0) and (t.amount > (avg_amt * 2))
        d['is_anomaly'] = is_high_val or is_spike
        
        transactions.append(d)

    alerts = []
    formatted_alerts = al_result.scalars().all()
    for a in formatted_alerts:
        d = a.__dict__.copy()
        d.pop('_sa_instance_state', None)
        alerts.append(d)

    # Dynamic Risk Rating
    risk_score = 0
    if len(alerts) > 0:
        risk_score += 1 # Has alerts
    if len(alerts) > 2:
        risk_score += 1 # Multiple alerts
    if any(t['amount'] > 100000 for t in transactions):
        risk_score += 1 # High value
        
    risk_rating = "LOW"
    if risk_score == 1: risk_rating = "MEDIUM"
    if risk_score >= 2: risk_rating = "HIGH"

    # Deduce customer info
    customer_name = "Unknown Customer"
    occupation = "Self-Employed / Retail"
    expected_turnover = 0.0
    
    if transactions:
        customer_name = transactions[0].get("description", "Unknown")
        
        # Refined Classification Logic
        is_receiving_salary = any(
            t.get("receiver_account") == account_number and 
            ("SALARY" in str(t.get("description", "")).upper() or "PAYROLL" in str(t.get("description", "")).upper())
            for t in transactions
        )
        is_sending_salary = any(
            t.get("sender_account") == account_number and 
            ("SALARY" in str(t.get("description", "")).upper() or "PAYROLL" in str(t.get("description", "")).upper())
            for t in transactions
        )

        if is_receiving_salary:
            occupation = "Salaried Employee (Retail)"
            salary_txs = [t['amount'] for t in transactions if t.get("receiver_account") == account_number and "SALARY" in str(t.get("description", "")).upper()]
            expected_turnover = max(salary_txs) if salary_txs else 0.0
        elif is_sending_salary:
            occupation = "Corporate / Payroll Entity"
            total_payroll = sum(t['amount'] for t in transactions if t.get("sender_account") == account_number and "SALARY" in str(t.get("description", "")).upper())
            expected_turnover = total_payroll
        
        # If turnover still 0, estimate from activity
        if expected_turnover == 0 and transactions:
            expected_turnover = sum(t['amount'] for t in transactions) / len(transactions) * 2

    return {
        "account_number": account_number,
        "customer": {
            "customer_id": f"CUST-{account_number}",
            "name": customer_name,
            "account_number": account_number,
            "risk_rating": risk_rating,
            "kyc_status": "VERIFIED",
            "occupation": occupation,
            "expected_monthly_turnover": expected_turnover
        },
        "transactions": transactions,
        "alerts": alerts
    }
