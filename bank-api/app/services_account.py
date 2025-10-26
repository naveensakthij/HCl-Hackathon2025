# app/services_account.py

from sqlalchemy.orm import Session
from fastapi import HTTPException
from .schemas import AccountCreate # Relative import
from .db_crud import create_account, get_account_by_customer_and_type, get_last_account_id # Relative import
from .db_models import Account # Relative import
from .core_config import settings # Relative import
from decimal import Decimal
from typing import Dict, Any

# ... (rest of the logic functions remains the same)
def get_account_prefix(account_type: str) -> str:
    # ... logic unchanged ...
    prefixes = {
        "savings": settings.ACCOUNT_PREFIX_SAVINGS,
        "current": settings.ACCOUNT_PREFIX_CURRENT,
        "fd": settings.ACCOUNT_PREFIX_FD,
    }
    return prefixes.get(account_type, "")

# ... (rest of the logic remains the same, update all 'crud.' calls to just 'crud' if needed)
# ...

def create_new_bank_account(db: Session, account_in: AccountCreate) -> Account:
    
    # 1. Check for Account Existence (409 Conflict)
    existing_account = get_account_by_customer_and_type( # Changed from crud.get_... to local function
        db, customer_id=account_in.customer_id, account_type=account_in.account_type
    )
    # ... (rest of the logic unchanged) ...

    # 6. Create Account in DB
    # The dictionary keys/values remain the same
    db_create_data = {
        # ...
    }
    db_account = create_account(db, db_create_data) # Changed from crud.create_... to local function
    
    return db_account