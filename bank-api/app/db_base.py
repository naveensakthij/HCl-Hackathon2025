# app/db_base.py (Cleaned)

from sqlalchemy.orm import declarative_base

Base = declarative_base()

# ❌ REMOVE THIS LINE:
# from . import db_models