from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.models import Transaction, Customer, Alert

class GenerateRequest(BaseModel):
    customer: Customer
    transactions: List[Transaction]
    alerts: List[Alert]
    region: str = "US"
    typology: Optional[str] = None

class ExplainRequest(BaseModel):
    text_segment: str
    context: Optional[dict] = None

class BatchRequest(BaseModel):
    requests: List[GenerateRequest]
    priority: str = "NORMAL"
