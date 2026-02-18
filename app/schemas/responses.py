from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class SARResponse(BaseModel):
    sar_id: str
    content: str
    sections: dict
    generated_at: datetime
    status: str

class GenerateResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    result: Optional[SARResponse] = None
    error: Optional[str] = None

class BatchStatusResponse(BaseModel):
    batch_id: str
    status: str
    progress: int
    details: Dict[str, int]

class Case(BaseModel):
    account_number: str
    customer_id: str
    customer_name: str
    risk_rating: str
    alert_count: int
    typology: str
    status: str

class CaseList(BaseModel):
    cases: List[Case]
