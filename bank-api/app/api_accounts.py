# app/api_accounts.py (Corrected Code)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from .db_session import get_db

# FIX: Use the dot (.) to indicate a module in the same package (the 'app' folder)
from .schemas import AccountCreate, AccountResponse 
from .services_account import create_new_bank_account 

# The router object
router = APIRouter()

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account_endpoint(
    account_in: AccountCreate, 
    db: Session = Depends(get_db)
):
    """Creates a new bank account."""
    db_account = create_new_bank_account(db, account_in)
    return db_account