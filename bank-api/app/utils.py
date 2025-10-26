# app/utils.py (CORRECTED CODE)

from sqlalchemy.orm import Session
from sqlalchemy import func
# We will use type hinting string and import inside the function to avoid circular imports

ACCOUNT_PREFIXES = {
    "savings": "SB-",
    "current": "CR-",
    "fd": "FD-",
}

def get_next_sequence_number(db: Session) -> int:
    """
    Finds the highest existing account ID and returns the next number.
    NOTE: Import moved inside the function to break potential circular dependencies.
    """
    from .db_models import Account # Import Account model here
    
    # Use max() function to find the highest existing ID
    max_id = db.query(func.max(Account.id)).scalar()
    
    # If the table is empty (max_id is None), start at 1, otherwise increment max_id
    next_id = (max_id or 0) + 1
    return next_id

def generate_account_number(db: Session, account_type: str) -> str:
    """
    Generates a unique, padded account number based on the account type.
    Format: PREFIX-0000000001
    """
    prefix = ACCOUNT_PREFIXES.get(account_type, "GEN-")
    
    # Get the next sequence number from the database
    sequence_num = get_next_sequence_number(db)
    
    # Pad the number to 10 digits
    padded_suffix = str(sequence_num).zfill(10)
    
    return f"{prefix}{padded_suffix}"