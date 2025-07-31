import os
from pydantic_settings import BaseSettings
from typing import ClassVar
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    ENV: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL","")
    
    # Celery
    #CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    #CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    SECRET_KEY: str = os.getenv("SECRET_KEY","eepyuppie")
    ACCESS_TOKEN_EXPIRE_MINUTES: ClassVar[int] = 21600
    ALGORITHM: ClassVar[str] = "HS256"
    
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Zotero / Mendeley credentials (if using OAuth)
    #ZOTERO_API_KEY: str = os.getenv("ZOTERO_API_KEY", "")
    #ZOTERO_USER_ID: str = os.getenv("ZOTERO_USER_ID", "")
    
    class Config:
        env_file = ".env"

settings = Settings()
