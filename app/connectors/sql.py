import pandas as pd
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.connectors.base import BaseConnector

class SQLConnector(BaseConnector):
    """
    Universal SQL Connector (PostgreSQL, MySQL, Oracle, SQL Server).
    Relies on SQLAlchemy for abstraction.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.connection_string = config.get("connection_string")
        self.engine = None

    async def connect(self):
        if not self.engine:
            self.engine = create_async_engine(self.connection_string, echo=True)

    async def disconnect(self):
        if self.engine:
            await self.engine.dispose()
            self.engine = None

    async def fetch_data(self, query: str = None, params: dict = None) -> pd.DataFrame:
        if not self.engine:
            await self.connect()
        
        async with self.engine.connect() as conn:
            result = await conn.execute(text(query), params or {})
            # Convert to DataFrame
            # Note: pandas read_sql does not support async engines directly easily
            # We fetch all and convert. For large datasets, we might need chunking.
            rows = result.fetchall()
            columns = result.keys()
            df = pd.DataFrame(rows, columns=columns)
            return df

    async def get_schema(self) -> dict:
        # Simplified schema retrieval
        return {"type": "sql", "dialect": self.engine.dialect.name if self.engine else "unknown"}
