# app/core_config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    
    ACCOUNT_PREFIX_SAVINGS: str = "SB"
    ACCOUNT_PREFIX_CURRENT: str = "CR"
    ACCOUNT_PREFIX_FD: str = "FD"
    
    MIN_DEPOSIT_SAVINGS: int = 500
    MIN_DEPOSIT_CURRENT: int = 1000
    MIN_DEPOSIT_FD: int = 5000

    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

settings = Settings()