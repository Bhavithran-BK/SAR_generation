from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

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

class SAR(Base):
    __tablename__ = "sars"
    
    sar_id = Column(String, primary_key=True, index=True)
    customer_id = Column(String, index=True)
    status = Column(String, default="DRAFT") # DRAFT, GENERATED, SUBMITTED
    content = Column(String, nullable=True) # Full SAR text/JSON
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    alerts = relationship("Alert", backref="sar")

class AuditBlock(Base):
    __tablename__ = "audit_log"
    
    block_id = Column(String, primary_key=True)
    previous_hash = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    action = Column(String)
    user_id = Column(String)
    data_hash = Column(String)
