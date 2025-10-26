# app/main.py (FINAL VERSION)

from fastapi import FastAPI
from .db_base import Base
from .db_session import engine

# ⚠️ CRITICAL FIX: Explicitly import the models file to guarantee
#    SQLAlchemy knows about the table definitions during startup.
from . import db_models 

# The router import
from .api_accounts import router as accounts_router 


# --- FastAPI Application Setup ---
app = FastAPI(
    title="Bank Account Creation API",
    description="A service for creating savings, current, and fixed deposit accounts with validation.",
    version="1.0.0",
)

# Use the startup event to create tables (as previously implemented)
@app.on_event("startup")
def startup_event():
    """Create all database tables when the application starts."""
    Base.metadata.create_all(bind=engine) 

# Router Inclusion
app.include_router(accounts_router, prefix="/api/v1/accounts", tags=["accounts"])

@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Welcome to the Bank Account Creation API. Documentation available at /docs"}