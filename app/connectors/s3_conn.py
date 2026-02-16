import pandas as pd
import boto3
import io
from app.connectors.base import BaseConnector
from app.core.config import settings

class S3Connector(BaseConnector):
    """
    Connector for AWS S3.
    """
    def __init__(self, config: dict):
        super().__init__(config)
        self.bucket = config.get("bucket", settings.S3_BUCKET_NAME)
        self.key = config.get("key")
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )

    async def connect(self):
        # Verify bucket access
        pass

    async def disconnect(self):
        pass

    async def fetch_data(self, query: str = None, params: dict = None) -> pd.DataFrame:
        # 'query' could be S3 Select in future
        response = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
        content = response["Body"].read()
        return pd.read_csv(io.BytesIO(content))

    async def get_schema(self) -> dict:
        return {"source": "s3", "bucket": self.bucket, "key": self.key}
