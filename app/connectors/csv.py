import pandas as pd
import aiofiles
from app.connectors.base import BaseConnector

class CSVConnector(BaseConnector):
    """
    Connector for CSV files (local or remote if extended).
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.file_path = config.get("file_path")

    async def connect(self):
        # File access check could go here
        pass

    async def disconnect(self):
        pass

    async def fetch_data(self, query: str = None, params: dict = None) -> pd.DataFrame:
        # 'query' here could be used for filtering, but for now we load the whole CSV
        # Using run_in_executor for pandas io operations which are blocking
        try:
             df = pd.read_csv(self.file_path)
             return df
        except Exception as e:
            print(f"Error reading CSV: {e}")
            raise e

    async def get_schema(self) -> dict:
        df = pd.read_csv(self.file_path, nrows=0)
        return {"columns": list(df.columns)}
