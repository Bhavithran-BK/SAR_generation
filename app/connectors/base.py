from abc import ABC, abstractmethod
from typing import List, Any
import pandas as pd

class BaseConnector(ABC):
    """
    Abstract base class for all data connectors.
    """
    
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    async def connect(self):
        """Establish connection to the data source."""
        pass

    @abstractmethod
    async def disconnect(self):
        """Close connection to the data source."""
        pass

    @abstractmethod
    async def fetch_data(self, query: str = None, params: dict = None) -> pd.DataFrame:
        """
        Fetch data from the source and return as a Pandas DataFrame.
        """
        pass
    
    @abstractmethod
    async def get_schema(self) -> dict:
        """Return the schema of the data source."""
        pass
