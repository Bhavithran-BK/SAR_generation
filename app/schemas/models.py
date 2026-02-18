from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

class Customer(BaseModel):
    customer_id: str
    name: str
    email: Optional[EmailStr] = None
    account_number: str
    risk_rating: str = "LOW"
    kyc_status: str = "VERIFIED"
    occupation: str = "Retail Customer"
    expected_monthly_turnover: float = 50000.0

class Transaction(BaseModel):
    transaction_id: str
    amount: float
    currency: str = "USD"
    timestamp: datetime
    sender_account: str
    receiver_account: str
    description: Optional[str] = None
    transaction_type: str = "WIRE"

class Alert(BaseModel):
    alert_id: str
    rule_name: str
    severity: str  # HIGH, MEDIUM, LOW
    timestamp: datetime
    details: dict

class AuditBlock(BaseModel):
    block_id: str
    previous_hash: str
    timestamp: datetime
    action: str
    user_id: str
    data_hash: str
