import pytest
from decimal import Decimal
from unittest.mock import MagicMock
from fastapi import HTTPException
from app.services_account import (
    create_new_bank_account,
    get_account_prefix,
    validate_deposit,
    generate_account_number
)
from app.schemas import AccountCreate
from app.db_models import Account
from app.core_config import settings
from fastapi.testclient import TestClient
from app.main import app # Import the FastAPI app for integration testing

# --- FIXTURES AND SETUP ---

@pytest.fixture
def mock_db_session():
    """Provides a mocked SQLAlchemy Session."""
    return MagicMock()

@pytest.fixture(autouse=True) # autouse=True ensures settings are reset before every test
def mock_settings():
    """Ensures consistent, known settings for testing business rules."""
    settings.MIN_DEPOSIT_SAVINGS = 500
    settings.MIN_DEPOSIT_CURRENT = 1000
    settings.MIN_DEPOSIT_FD = 5000
    settings.ACCOUNT_PREFIX_SAVINGS = "SB"
    settings.ACCOUNT_PREFIX_CURRENT = "CR"
    settings.ACCOUNT_PREFIX_FD = "FD"
    return settings

# --- CORE LOGIC TESTS ---

def test_generate_account_number_boundary():
    """Tests account number padding and boundary cases."""
    # Test case 1: Starting from 0
    assert generate_account_number("savings", 0) == "SB-0000000001"
    # Test case 2: Near the 10-digit boundary (ensures padding is right)
    assert generate_account_number("current", 9999999999) == "CR-10000000000"

def test_validate_deposit_success_all_types():
    """Tests successful validation for minimum deposit and FD requirements."""
    # Savings (boundary condition: exact minimum)
    validate_deposit("savings", Decimal("500.00"), {}) 
    # Current (above minimum)
    validate_deposit("current", Decimal("1000.01"), {}) 
    # FD (exact minimum, valid months)
    validate_deposit("fd", Decimal("5000.00"), {"maturity_months": 3}) 

# --- BUSINESS RULE FAILURE TESTS (Minimum Deposits) ---

@pytest.mark.parametrize("account_type, deposit, expected_min", [
    ("savings", Decimal("499.99"), 500),
    ("current", Decimal("999.99"), 1000),
    ("fd", Decimal("4999.99"), 5000),
])
def test_validate_deposit_failure_min_boundary(account_type, deposit, expected_min):
    """Tests failure when deposit is one cent/rupee below the minimum for all types."""
    with pytest.raises(HTTPException) as excinfo:
        validate_deposit(account_type, deposit, {"maturity_months": 1} if account_type == 'fd' else {})
    assert excinfo.value.status_code == 400
    assert f"at least ₹{expected_min:.2f}" in str(excinfo.value.detail)

# --- BUSINESS RULE FAILURE TESTS (FD Specific) ---

@pytest.mark.parametrize("maturity_months, error_detail", [
    (None, "require a 'maturity_months'"),
    (0, "require a 'maturity_months'"),
    (-1, "require a 'maturity_months'"),
])
def test_validate_deposit_fd_failure_maturity_edge_cases(maturity_months, error_detail):
    """Tests failure for FD when maturity_months is missing or invalid."""
    with pytest.raises(HTTPException) as excinfo:
        validate_deposit("fd", Decimal("5000.00"), {"maturity_months": maturity_months})
        
    assert excinfo.value.status_code == 400
    assert error_detail in str(excinfo.value.detail)

# --- SERVICE LAYER TESTS (Database Interaction) ---

@pytest.fixture
def mock_account_in():
    """Provides a valid input schema object for testing."""
    return AccountCreate(
        customer_id="TESTCUST1", 
        account_type="savings", 
        initial_deposit=Decimal("1000.00"), 
        currency="INR"
    )

def test_create_new_bank_account_success(mock_db_session, mocker, mock_account_in):
    """Tests successful account creation, verifying the core logic flow and number generation."""
    
    # Mocks: No existing account, last ID is 99
    mocker.patch('app.db_crud.get_account_by_customer_and_type', return_value=None)
    mocker.patch('app.db_crud.get_last_account_id', return_value=99)
    
    # Mock the return value of create_account
    mock_account = MagicMock(spec=Account)
    mock_account.account_number = "SB-0000000100"
    mock_account.customer_id = "TESTCUST1"
    mocker.patch('app.db_crud.create_account', return_value=mock_account)

    new_account = create_new_bank_account(mock_db_session, mock_account_in)

    # Assertions
    assert new_account.account_number == "SB-0000000100"
    mocker.patch('app.db_crud.create_account').assert_called_once()
    mocker.patch('app.db_crud.get_last_account_id').assert_called_once()


def test_create_new_bank_account_failure_conflict(mock_db_session, mocker, mock_account_in):
    """Tests the 409 CONFLICT scenario where a duplicate account exists."""
    
    # Mock crud functions: Simulate finding an existing account
    mocker.patch('app.db_crud.get_account_by_customer_and_type', return_value=MagicMock())
    
    with pytest.raises(HTTPException) as excinfo:
        create_new_bank_account(mock_db_session, mock_account_in)
        
    assert excinfo.value.status_code == 409
    assert "already exists" in str(excinfo.value.detail)

# --- API INTEGRATION TEST (Verifies Router/Endpoint Works) ---

@pytest.fixture
def client():
    """Provides a TestClient instance for API integration testing."""
    return TestClient(app)

def test_api_post_valid_request(client, mocker):
    """Tests the main API endpoint with a valid request and mocks service success."""
    
    # Mock the service function to return a mock response object
    mock_response_data = {
        "id": 1,
        "account_number": "SB-TESTNUM",
        "customer_id": "APITEST",
        "account_type": "savings",
        "balance": "1000.00",
        "currency": "INR",
        "created_at": "2023-01-01T00:00:00+00:00",
        "extra_data": None
    }
    
    # Use mocker to replace the service function with a mock
    mocker.patch(
        'app.api_accounts.create_new_bank_account', 
        return_value=mock_response_data
    )

    response = client.post(
        "/api/v1/accounts",
        json={
            "customer_id": "APITEST", 
            "account_type": "savings", 
            "initial_deposit": 1000.00
        }
    )
    
    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["customer_id"] == "APITEST"
    assert "account_number" in data
    
def test_api_post_invalid_schema(client):
    """Tests API endpoint failure due to Pydantic schema validation."""
    
    # Deposit is zero, which fails the 'gt=0' check in AccountCreate
    response = client.post(
        "/api/v1/accounts",
        json={
            "customer_id": "APITEST", 
            "account_type": "savings", 
            "initial_deposit": 0.00 # Invalid input
        }
    )
    
    # Assertions
    assert response.status_code == 422 # 422 Unprocessable Entity for Pydantic validation errors
    data = response.json()
    assert "value_error" in data["detail"][0]["type"]
    assert "greater than 0" in data["detail"][0]["msg"]