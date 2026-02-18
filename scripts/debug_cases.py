import asyncio
from app.db.base import AsyncSessionLocal
from sqlalchemy import select
from app.models.sql import Transaction, Alert

async def debug_case(account_number):
    async with AsyncSessionLocal() as db:
        tx_query = select(Transaction).where(
            (Transaction.sender_account == account_number) | (Transaction.receiver_account == account_number)
        )
        al_query = select(Alert).where(Alert.account_number == account_number)
        
        tx_result = await db.execute(tx_query)
        al_result = await db.execute(al_query)
        
        transactions = tx_result.scalars().all()
        alerts = al_result.scalars().all()
        
        print(f"Found {len(transactions)} txs")
        
        # Try to serialize exactly like cases.py
        try:
            tx_clean = []
            for t in transactions:
                d = t.__dict__.copy()
                d.pop('_sa_instance_state', None)
                tx_clean.append(d)
                
            al_clean = []
            for a in alerts:
                d = a.__dict__.copy()
                d.pop('_sa_instance_state', None)
                al_clean.append(d)
                
            response = {
                "account_number": account_number,
                "customer": {
                    "customer_id": f"CUST-{account_number}",
                    "name": tx_clean[0].get("description", "Unknown") if tx_clean else "Unknown",
                    "risk_rating": "HIGH",
                    "kyc_status": "VERIFIED"
                },
                "transactions": tx_clean,
                "alerts": al_clean
            }
            
            import json
            # Use default=str to handle datetime
            json.dumps(response, default=str)
            print("Serialization OK")
            print(json.dumps(response, default=str, indent=2))
        except Exception as e:
            print(f"Serialization Failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_case("IN-882299"))
