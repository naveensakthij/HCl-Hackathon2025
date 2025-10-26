# HCl-Hackathon2025
Account Creation
# 🏦 Bank Account Creation API

A backend service built with **FastAPI**, **SQLAlchemy**, and **SQLite** that allows clients to create bank accounts (`savings`, `current`, `fd`). This project focuses on backend logic only—no frontend UI.

---

## 📚 Table of Contents

1. [Overview](#overview)
2. [Tech Stack](#tech-stack)
3. [Features](#features)
4. [API Endpoint](#api-endpoint)
5. [Database Model](#database-model)
6. [Validation Rules](#validation-rules)
7. [Account Number Format](#account-number-format)
8. [Project Structure](#project-structure)
9. [Setup Guide (Windows)](#setup-guide-windows)
10. [Environment Variables](#environment-variables)
11. [Running the Server](#running-the-server)
12. [Migrations](#migrations)
13. [Testing](#testing)
14. [Future Improvements](#future-improvements)

---

## 📘 Overview

This API allows users to create bank accounts with proper validation and stores them in a PostgreSQL database. It supports three account types:

- `savings`
- `current`
- `fd` (fixed deposit)

Each account is assigned a unique account number and validated based on business rules.

---

## 🧰 Tech Stack

- Python 3.10+
- FastAPI (web framework)
- SQLAlchemy (ORM)
- SQLite (database)
- Alembic (migrations)
- Pydantic (validation)
- Uvicorn (ASGI server)

---

## 🚀 Features

- Create accounts with type-specific validation
- Auto-generate unique account numbers
- Store account data in SQLite
- RESTful API with Swagger documentation

---

## 📬 API Endpoint

### POST `app/api_accounts.py`
\text{POST } \text{[http://127.0.0.1:8000/api/v1/accounts/](http://127.0.0.1:8000/api/v1/accounts/)}

Create a new bank account.

**Request Body:**

```json
{
  "customer_id": "CUST123",
  "account_type": "savings",
  "initial_deposit": 5000,
  "currency": "INR",
  "maturity_months": 12  // only for fd
}
```

**Response:**

```json
{
  "account_id": 1,
  "account_number": "SB-0000000001",
  "customer_id": "CUST123",
  "account_type": "savings",
  "balance": 5000,
  "currency": "INR",
  "created_at": "2025-10-26T05:20:30Z"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid input or deposit too low
- `409 Conflict`: Account already exists for customer/type

---

## 🗄️ Database Model

```python
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True)
    account_number = Column(String, unique=True, nullable=False)
    customer_id = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    balance = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="INR")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

## ✅ Validation Rules

| Account Type | Minimum Deposit | Extra Field |
|--------------|------------------|-------------|
| savings      | ₹500             | —           |
| current      | ₹1000            | —           |
| fd           | ₹5000            | `maturity_months >= 1` |

---

## 🔢 Account Number Format

- Prefix: `SB-`, `CR-`, `FD-`
- Suffix: 10-digit padded number (e.g., `SB-0000000001`)
- Generated using database sequence or last ID

---

## 📁 Project Structure
---
File: app/core/config.py
File: app/db/base.py
File: app/db/models.py
File: app/db/session.py
File: app/db/crud.py
File: app/schemas.py
File: app/services/account_service.py
File: app/api/v1/accounts.py
File: app/main.py (The final, corrected entry point)

---

## 🖥️ Setup Guide (Windows)

### 1. Install Tools
- Python 3.10+: [python.org](https://www.python.org/downloads/)
- VS Code: [code.visualstudio.com](https://code.visualstudio.com/)
- PostgreSQL: [postgresql.org](https://www.postgresql.org/download/)

### 2. Create Project Folder
Open VS Code → File → Open Folder → Create `bank-api`

### 3. Open Terminal
Click **Terminal → New Terminal**

### 4. Create Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+psycopg2://postgres:yourpassword@localhost:5432/bankdb
ACCOUNT_NUM_PREFIX=SB
MIN_DEPOSIT_SAVINGS=500
MIN_DEPOSIT_CURRENT=1000
MIN_DEPOSIT_FD=5000
```

Replace `yourpassword` with your actual PostgreSQL password.

---

## ▶️ Running the Server

```bash
uvicorn app.main:app --reload
or
python -m uvicorn app.main:app --reload
```

Visit: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧬 Migrations (Alembic)

### Initialize Alembic
```bash
alembic init alembic
```

### Create Migration
```bash
alembic revision --autogenerate -m "create accounts table"
alembic upgrade head
```

---

## 🧪 Testing

Use `pytest` for unit tests.

Example:
```python
def test_invalid_deposit():
    with pytest.raises(ValueError):
        validate_deposit("savings", 100)
```

---

## 🔮 Future Improvements

- Add JWT authentication
- Add deposit/withdraw endpoints
- Add transaction ledger
- Add audit logs
- Add rate limiting and logging

---
