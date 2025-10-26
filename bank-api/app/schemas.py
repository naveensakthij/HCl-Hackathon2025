# app/schemas.py

from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, field_validator, Field
from decimal import Decimal

# Define supported account types
AccountType = Literal["savings", "current", "fd"]

class AccountCreate(BaseModel):
    customer_id: str = Field(..., max_length=50)
    account_type: AccountType
    # Deposit must be greater than zero and have 2 decimal places
    initial_deposit: Decimal = Field(..., gt=0, decimal_places=2) 
    currency: str = Field("INR", max_length=3)
    # Optional field, but required conditionally for FD, must be >= 1
    maturity_months: Optional[int] = Field(None, ge=1, description="Required for 'fd' account type.")

    # Pydantic Validator to enforce FD rule
    @field_validator('maturity_months', mode='before')
    @classmethod
    def check_maturity_for_fd(cls, v, info):
        # We check the account_type provided in the entire request data (info.data)
        values = info.data
        
        if values.get('account_type') == 'fd':
            # v is None if maturity_months was completely omitted
            if v is None or v == 0 or v < 1: 
                raise ValueError('FD accounts require maturity_months (minimum 1 month).')
        
        return v
    
    model_config = {'from_attributes': True}

# Response Schema (Used in api_accounts.py)
class AccountResponse(BaseModel):
    account_id: int
    account_number: str
    customer_id: str
    account_type: AccountType
    balance: Decimal
    currency: str
    created_at: datetime
    
    model_config = {'from_attributes': True}