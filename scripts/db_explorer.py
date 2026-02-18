import asyncio
import os
from sqlalchemy import select
from app.db.base import engine, AsyncSessionLocal
from app.models.sql import Transaction, Alert, SAR, User

async def explore():
    print("\n=== DATABASE EXPLORER ===\n")
    
    async with AsyncSessionLocal() as session:
        # 1. Transactions
        print("--- TOP 10 TRANSACTIONS ---")
        tx_q = select(Transaction).limit(10)
        tx_res = await session.execute(tx_q)
        for tx in tx_res.scalars().all():
            print(f"ID: {tx.transaction_id} | Amt: {tx.amount} | From: {tx.sender_account} | To: {tx.receiver_account} | Desc: {tx.description}")
        
        # 2. Alerts
        print("\n--- ACTIVE ALERTS ---")
        al_q = select(Alert)
        al_res = await session.execute(al_q)
        for al in al_res.scalars().all():
            print(f"ID: {al.alert_id} | Rule: {al.rule_name} | Account: {al.account_number} | Sev: {al.severity}")
            
        # 3. SARs (Generated Reports)
        print("\n--- GENERATED SARs ---")
        sar_q = select(SAR)
        sar_res = await session.execute(sar_q)
        for s in sar_res.scalars().all():
            print(f"SAR ID: {s.sar_id} | Cust: {s.customer_id} | Status: {s.status} | Created: {s.generated_at}")

        # 4. Users
        print("\n--- SYSTEM USERS ---")
        u_q = select(User)
        u_res = await session.execute(u_q)
        for u in u_res.scalars().all():
            print(f"User: {u.username} | Role: {u.role}")

    print("\n=== END OF DUMP ===\n")

if __name__ == "__main__":
    # Ensure PYTHONPATH is set so 'app' can be imported
    # (The caller should handle this, or we can use a wrapper)
    asyncio.run(explore())
