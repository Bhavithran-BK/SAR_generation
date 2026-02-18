from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(String, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    timestamp = Column(DateTime, default=datetime.utcnow)
    sender_account = Column(String, index=True)
    receiver_account = Column(String, index=True)
    description = Column(String, nullable=True)
    transaction_type = Column(String, default="WIRE")

class Alert(Base):
    __tablename__ = "alerts"
    
    alert_id = Column(String, primary_key=True)
    rule_name = Column(String)
    severity = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(JSON)
    sar_id = Column(String, ForeignKey("sars.sar_id"), nullable=True)
    account_number = Column(String, index=True) # Link alert to a specific account/case

class SAR(Base):
    __tablename__ = "sars"
    
    sar_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    status = Column(String, default="GENERATED") # GENERATED, REVIEWED, VERIFIED, FINALIZED
    content = Column(String, nullable=True) # AI-generated narrative
    edited_content = Column(String, nullable=True) # Manual edits
    
    officer_id = Column(String, nullable=True)
    auditor_id = Column(String, nullable=True)
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    finalized_at = Column(DateTime, nullable=True)
    
    alerts = relationship("Alert", backref="sar")

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String) # OFFICER, AUDITOR

class AuditBlock(Base):
    __tablename__ = "audit_log"
    
    block_id = Column(String, primary_key=True)
    previous_hash = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String)
    user_id = Column(String)
    data_hash = Column(String)
