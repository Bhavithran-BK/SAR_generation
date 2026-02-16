from app.connectors.sql import SQLConnector
from app.connectors.csv import CSVConnector
from app.connectors.json_conn import JSONConnector
from app.connectors.s3_conn import S3Connector

class ConnectorFactory:
    @staticmethod
    def get_connector(connector_type: str, config: dict):
        if connector_type == "sql":
            return SQLConnector(config)
        elif connector_type == "csv":
            return CSVConnector(config)
        elif connector_type == "json":
            return JSONConnector(config)
        elif connector_type == "s3":
            return S3Connector(config)
        else:
            raise ValueError(f"Unknown connector type: {connector_type}")
