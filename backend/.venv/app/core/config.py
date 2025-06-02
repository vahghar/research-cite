import os
from pydantic_settings import BaseSettings
from typing import ClassVar

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = "True"
    
    # Database
    DATABASE_URL: str = "postgresql://neondb_owner:npg_DfwBQz6OoUF1@ep-wispy-frost-a8nbhxcx-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    SECRET_KEY: ClassVar[str] = "kS9$h4Xw3BvT!mC7uL@zPf2R^gQxD*Nj"
    ACCESS_TOKEN_EXPIRE_MINUTES: ClassVar[int] = 60
    ALGORITHM: ClassVar[str] = "HS256"
    
    # Zotero / Mendeley credentials (if using OAuth)
    #ZOTERO_API_KEY: str = os.getenv("ZOTERO_API_KEY", "")
    #ZOTERO_USER_ID: str = os.getenv("ZOTERO_USER_ID", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
