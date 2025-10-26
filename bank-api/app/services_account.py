# app/services_account.py

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from decimal import Decimal
from .schemas import AccountCreate, AccountResponse
from .db_models import Account  # Assuming your SQLAlchemy models are here
from .core_config import settings # Import config for deposit mins
from .utils import generate_account_number # Placeholder for your utility function


def validate_deposit(account_type: str, deposit: Decimal):
    """Checks if the initial deposit meets the minimum requirement based on type."""
    
    min_deposit_map = {
        "savings": settings.MIN_DEPOSIT_SAVINGS,
        "current": settings.MIN_DEPOSIT_CURRENT,
        "fd": settings.MIN_DEPOSIT_FD,
    }

    min_amount = min_deposit_map.get(account_type)
    
    if deposit < min_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Initial deposit of {deposit:.2f} is below the minimum required amount of {min_amount:.2f} for a {account_type} account."
        )


def create_new_bank_account(db: Session, account_in: AccountCreate) -> Account:
    """
    Performs final validation and creates a new account record.
    """
    
    # 1. Run business logic validation (minimum deposit check)
    validate_deposit(account_in.account_type, account_in.initial_deposit)

    # 2. Generate account number (Assumes generate_account_number function exists)
    # NOTE: You'll need to create this utility function in app/utils.py
    new_account_number = generate_account_number(db, account_in.account_type)

    # 3. Prepare metadata for FD (maturity months)
    metadata_data = None
    if account_in.account_type == 'fd':
        metadata_data = {'maturity_months': account_in.maturity_months}
    
    # 4. Create the SQLAlchemy model instance
    db_account = Account(
        account_number=new_account_number,
        customer_id=account_in.customer_id,
        account_type=account_in.account_type,
        balance=account_in.initial_deposit,
        currency=account_in.currency,
        metadata=metadata_data,
    )

    # 5. Commit to database
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account