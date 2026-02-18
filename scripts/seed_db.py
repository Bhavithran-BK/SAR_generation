import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select
from app.db.base import engine, Base, AsyncSessionLocal
from app.models.sql import Transaction, Alert, SAR, User

async def seed():
    async with engine.begin() as conn:
        print("Recreating database schema...")
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        print("Seeding cases...")
        
        # Case 1: Mumbai High Value Trade
        acc1 = "IN-882299"
        cust1 = "Mumbai Trading Co"
        txns1 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=1200000.0, currency="INR", sender_account="EXT-001", receiver_account=acc1, transaction_type="WIRE", description="Business Payment"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=950000.0, currency="INR", sender_account=acc1, receiver_account="EXT-002", transaction_type="WIRE", description="Supplier Settlement")
        ]
        alert1 = Alert(alert_id="ALT-001", rule_name="High Value Foreign Inflow", severity="HIGH", details={"threshold": 1000000}, account_number=acc1)
        
        # Case 2: Bangalore Tech Smurfing
        acc2 = "IN-773311"
        cust2 = "Anand Sharma"
        txns2 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=98000.0, currency="INR", sender_account="CASH", receiver_account=acc2, transaction_type="CASH_DEPOSIT"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=96000.0, currency="INR", sender_account="CASH", receiver_account=acc2, transaction_type="CASH_DEPOSIT"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=94000.0, currency="INR", sender_account="CASH", receiver_account=acc2, transaction_type="CASH_DEPOSIT")
        ]
        alert2 = Alert(alert_id="ALT-002", rule_name="Structuring Pattern", severity="MEDIUM", details={"limit": 100000}, account_number=acc2)

        # Case 3: Delhi NGO Rapid Transfer
        acc3 = "IN-665544"
        cust3 = "SafeHands Foundation"
        txns3 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=500000.0, currency="INR", sender_account="DONOR-A", receiver_account=acc3, transaction_type="NEFT"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=495000.0, currency="INR", sender_account=acc3, receiver_account="OFFSHORE-X", transaction_type="WIRE")
        ]
        alert3 = Alert(alert_id="ALT-003", rule_name="Rapid In-Out Flow", severity="CRITICAL", details={"timeframe": "2 hours"}, account_number=acc3)

        session.add_all(txns1 + txns2 + txns3)
        session.add_all([alert1, alert2, alert3])

        # Case 4: Chennai Gold Import (High Value Structuring)
        acc4 = "IN-559900"
        txns4 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=2500000.0, currency="INR", sender_account="EXT-DUBAI", receiver_account=acc4, transaction_type="WIRE", description="Import Advance"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=20000.0, currency="INR", sender_account=acc4, receiver_account="CASH", transaction_type="ATM", description="Cash Withdrawal"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=20000.0, currency="INR", sender_account=acc4, receiver_account="CASH", transaction_type="ATM", description="Cash Withdrawal"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=1500000.0, currency="INR", sender_account=acc4, receiver_account="JEWELER-X", transaction_type="RTGS", description="Purchase of Bullion")
        ]
        alert4 = Alert(alert_id="ALT-004", rule_name="Inconsistent Trade Pattern", severity="HIGH", details={"discrepancy": "High Cash vs Trade"}, account_number=acc4)

        # Case 5: Hyderabad Round Tripping
        acc5 = "IN-442211"
        txns5 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=5000000.0, currency="INR", sender_account=acc5, receiver_account="SHELL-CORP-A", transaction_type="WIRE", description="Consulting Fees"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=4800000.0, currency="INR", sender_account="SHELL-CORP-B", receiver_account=acc5, transaction_type="WIRE", description="Investment Return")
        ]
        alert5 = Alert(alert_id="ALT-005", rule_name="Round Tripping of Funds", severity="CRITICAL", details={"source": "Shell Entity"}, account_number=acc5)

        # Case 6: Kolkata Mule Account
        acc6 = "IN-110022"
        txns6 = []
        # Generate 10 small incoming txns
        for i in range(10):
            txns6.append(Transaction(transaction_id=str(uuid.uuid4()), amount=49000.0, currency="INR", sender_account=f"UPI-USER-{i}", receiver_account=acc6, transaction_type="UPI", description="Peer Transfer"))
        # One large outgoing
        txns6.append(Transaction(transaction_id=str(uuid.uuid4()), amount=480000.0, currency="INR", sender_account=acc6, receiver_account="CRYPTO-EXCH", transaction_type="IMPS", description="Investment"))
        
        alert6 = Alert(alert_id="ALT-006", rule_name="Mule Account Activity", severity="HIGH", details={"pattern": "Many-to-One"}, account_number=acc6)

        session.add_all(txns4 + txns5 + txns6)
        session.add_all([alert4, alert5, alert6])

        # Case 7: High Risk Jurisdiction (Terror Financing)
        acc7 = "IN-998877"
        txns7 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=45000.0, currency="INR", sender_account="NGO-CHARITY", receiver_account=acc7, transaction_type="WIRE", description="Donation"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=40000.0, currency="INR", sender_account=acc7, receiver_account="UNKNOWN-BORDER-ENT", transaction_type="HAWALA", description="Relief Aid")
        ]
        alert7 = Alert(alert_id="ALT-007", rule_name="Terror Financing Indicators", severity="CRITICAL", details={"region": "High Risk Border Zone"}, account_number=acc7)

        # Case 8: Crypto P2P Network
        acc8 = "IN-334455"
        txns8 = []
        for i in range(5):
             txns8.append(Transaction(transaction_id=str(uuid.uuid4()), amount=150000.0, currency="INR", sender_account=acc8, receiver_account=f"P2P-EXCH-{i}", transaction_type="USDT_BUY", description="Crypto Purchase"))
        alert8 = Alert(alert_id="ALT-008", rule_name="High Velocity Crypto", severity="HIGH", details={"volume": "7.5L in 1 hour"}, account_number=acc8)

        # Case 9: Elder Exploitation
        acc9 = "IN-123123"
        txns9 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=2500000.0, currency="INR", sender_account="RETIREMENT-FUND", receiver_account=acc9, transaction_type="NEFT", description="Pension Lump Sum"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=2500000.0, currency="INR", sender_account=acc9, receiver_account="CARETAKER-JOINT", transaction_type="INTERNAL", description="Transfer to Joint Acct")
        ]
        alert9 = Alert(alert_id="ALT-009", rule_name="Vulnerable Customer Activity", severity="MEDIUM", details={"age": "82", "typology": "Sudden Depletion"}, account_number=acc9)

        # Case 10: Payroll Padding (Shell Companies)
        acc10 = "IN-654321"
        txns10 = []
        for i in range(15):
            txns10.append(Transaction(transaction_id=str(uuid.uuid4()), amount=25000.0, currency="INR", sender_account=acc10, receiver_account=f"EMP-{i}", transaction_type="SALARY", description="Salary Oct"))
        alert10 = Alert(alert_id="ALT-010", rule_name="Ghost Employees", severity="HIGH", details={"anomaly": "Non-existent Tax IDs"}, account_number=acc10)

        session.add_all(txns7 + txns8 + txns9 + txns10)
        session.add_all([alert7, alert8, alert9, alert10])

        # Case 11: Student Account (Low Risk - No Alerts)
        acc11 = "IN-202020"
        txns11 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=1500.0, currency="INR", sender_account="PARENT", receiver_account=acc11, transaction_type="UPI", description="Pocket Money"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=200.0, currency="INR", sender_account=acc11, receiver_account="CAFE-XX", transaction_type="UPI", description="Coffee"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=500.0, currency="INR", sender_account=acc11, receiver_account="BOOKSTORE", transaction_type="UPI", description="Books")
        ]
        # No alerts for this case

        # Case 12: Salary Account (Clean - Medium Volume)
        acc12 = "IN-303030"
        txns12 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=85000.0, currency="INR", sender_account="CORP-EMPLOYER", receiver_account=acc12, transaction_type="NEFT", description="Salary Nov"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=15000.0, currency="INR", sender_account=acc12, receiver_account="RENT-LANDLORD", transaction_type="UPI", description="Rent"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=5000.0, currency="INR", sender_account=acc12, receiver_account="SIP-FUND", transaction_type="ACH", description="Mutual Fund SIP")
        ]
        # No alerts

        # Case 13: High Value Director Salary (Context Test)
        acc13 = "IN-404040"
        txns13 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=550000.0, currency="INR", sender_account="TECH-GIANT-CORP", receiver_account=acc13, transaction_type="NEFT", description="DIRECTOR SALARY OCT"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=550000.0, currency="INR", sender_account="TECH-GIANT-CORP", receiver_account=acc13, transaction_type="NEFT", description="DIRECTOR SALARY NOV"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=200000.0, currency="INR", sender_account=acc13, receiver_account="BMW-DEALER", transaction_type="RTGS", description="CAR EMI")
        ]
        alert13 = Alert(alert_id="ALT-013", rule_name="Unexpected High Value Inflow", severity="MEDIUM", details={"threshold": 100000}, account_number=acc13)

        # Case 14: Salaried False Positive (Context Test)
        acc14 = "IN-505050"
        txns14 = [
            Transaction(transaction_id=str(uuid.uuid4()), amount=120000.0, currency="INR", sender_account="TCS-PAYROLL", receiver_account=acc14, transaction_type="NEFT", description="SALARY NOV"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=25000.0, currency="INR", sender_account=acc14, receiver_account="LANDLORD", transaction_type="UPI", description="RENT PAYMENT"),
            Transaction(transaction_id=str(uuid.uuid4()), amount=15000.0, currency="INR", sender_account="EXT-UK-PERSONAL", receiver_account=acc14, transaction_type="WIRE", description="BIRTHDAY GIFT FROM COUSIN")
        ]
        alert14 = Alert(alert_id="ALT-014", rule_name="Unexpected Foreign Inflow", severity="LOW", details={"source": "UK"}, account_number=acc14)

        session.add_all(txns11 + txns12 + txns13 + txns14)
        session.add_all([alert13, alert14])
        
        # --- SEED USERS ---
        users = [
            User(username="officer", password_hash="password", role="OFFICER"),
            User(username="auditor", password_hash="password", role="AUDITOR")
        ]
        
        for user in users:
            # Check if user already exists
            q = select(User).where(User.username == user.username)
            res = await session.execute(q)
            if not res.scalar_one_or_none():
                session.add(user)
        
        await session.commit()
        print("Database Seeded Successfully including Users.")

if __name__ == "__main__":
    asyncio.run(seed())
