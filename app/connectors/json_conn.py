import pandas as pd
import aiohttp
from app.connectors.base import BaseConnector

class JSONConnector(BaseConnector):
    """
    Connector for JSON data from REST APIs.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.url = config.get("url")
        self.headers = config.get("headers", {})

    async def connect(self):
        # Optional: check if API is reachable
        pass

    async def disconnect(self):
        pass

    async def fetch_data(self, query: str = None, params: dict = None) -> pd.DataFrame:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    # Assume data is a list of records or has a specific key 'data'
                    if isinstance(data, dict) and "data" in data:
                        data = data["data"]
                    return pd.DataFrame(data)
                else:
                    raise Exception(f"Failed to fetch data: {response.status}")

    async def get_schema(self) -> dict:
        # Schema inference from first record
        return {"type": "json_api", "url": self.url}
