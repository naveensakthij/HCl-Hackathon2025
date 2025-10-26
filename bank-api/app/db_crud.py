# app/db_crud.py

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, Dict, Any
from .db_models import Account # Relative import

def create_account(db: Session, account_in: Dict[str, Any]) -> Account:
    db_account = Account(**account_in)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_account_by_customer_and_type(db: Session, customer_id: str, account_type: str) -> Optional[Account]:
    return db.query(Account).filter(
        Account.customer_id == customer_id, 
        Account.account_type == account_type
    ).first()

def get_last_account_id(db: Session) -> int:
    max_id = db.query(func.max(Account.id)).scalar()
    return max_id if max_id is not None else 0