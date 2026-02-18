import asyncio
from app.db.base import engine
from sqlalchemy import select, text
from app.models.sql import Transaction, Alert, SAR

async def diagnos():
    async with engine.connect() as conn:
        # Check tables
        res = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [r[0] for r in res.all()]
        print(f"Tables: {tables}")
        
        # Check Alert counts
        res = await conn.execute(select(Alert))
        alerts = res.all()
        print(f"Alert count: {len(alerts)}")
        
        # Check Account Numbers
        res = await conn.execute(select(Alert.account_number).distinct())
        accs = [r[0] for r in res.all()]
        print(f"Distinct accounts: {accs}")

if __name__ == "__main__":
    asyncio.run(diagnos())
