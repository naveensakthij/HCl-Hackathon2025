# app/db_models.py

from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON, func
from .db_base import Base # Relative import

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, nullable=False, index=True)
    customer_id = Column(String, nullable=False, index=True)
    account_type = Column(String, nullable=False) 
    
    balance = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    
    extra_data = Column(JSON, nullable=True) 
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())