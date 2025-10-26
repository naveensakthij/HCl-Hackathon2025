# app/schemas.py

from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any
from datetime import datetime
from decimal import Decimal

# --- Request Schemas ---
class AccountCreateBase(BaseModel):
    """Base schema for creating a new account."""
    
    # Using standard 'str' and Field for constraints (Pydantic V2)
    customer_id: str = Field(
        ..., 
        min_length=5, 
        max_length=50, 
        description="Unique ID for the customer."
    )
    account_type: str = Field(
        ..., 
        description="Type of account: 'savings', 'current', or 'fd'."
    )
    initial_deposit: Decimal = Field(
        ..., 
        gt=0, 
        max_digits=12, 
        decimal_places=2, 
        description="Initial deposit amount (must be > 0)."
    )
    currency: str = Field(
        "INR", 
        min_length=3, 
        max_length=3
    )

class AccountCreate(AccountCreateBase):
    """Schema for the incoming POST request."""
    
    maturity_months: Optional[int] = Field(
        None, 
        ge=1, 
        description="Maturity period in months (only for 'fd' accounts)."
    )

    @model_validator(mode='before')
    @classmethod
    def validate_account_type(cls, data: Any) -> Any:
        """Ensures the account type is one of the supported values."""
        if not isinstance(data, dict):
            return data
            
        account_type = data.get('account_type')
        if account_type and account_type not in ('savings', 'current', 'fd'):
            raise ValueError(
                'Invalid account_type. Must be "savings", "current", or "fd".'
            )
        return data

# --- Response Schema ---
class AccountResponse(BaseModel):
    """Schema for the outgoing JSON response."""
    
    id: int 
    account_number: str
    customer_id: str
    account_type: str
    balance: Decimal = Field(max_digits=12, decimal_places=2)
    currency: str
    created_at: datetime
    # Matches the renamed field in the SQLAlchemy model
    extra_data: Optional[Any] 

    # Pydantic V2 configuration for reading data from SQLAlchemy models (ORM)
    model_config = {
        'from_attributes': True,
    }