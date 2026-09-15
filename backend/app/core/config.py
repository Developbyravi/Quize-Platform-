import os
from pydantic_settings import BaseSettings
from typing import List, Union, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Engineering Day Coding Challenge"
    SUBTITLE: str = "Engineering Day 2026 — Coding Competition"
    API_V1_STR: str = "/api"
    
    # Security & Auth
    SECRET_KEY: str = "engday2026_super_secret_key_change_in_production_123456789"
    JWT_SECRET: str = "engday2026_jwt_secret_key_change_in_production_987654321"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ADMIN_EMAIL: Optional[str] = None
    ADMIN_PASSWORD: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    
    # Judge0 Integration
    JUDGE0_URL: str = "https://judge0-ce.p.rapidapi.com"
    JUDGE0_API_KEY: str = ""
    JUDGE0_HOST: str = "judge0-ce.p.rapidapi.com"
    JUDGE0_TIMEOUT: int = 15  # seconds
    
    # Rate Limiting Defaults
    RUN_CODE_RATE_LIMIT_SEC: int = 3
    SUBMIT_CODE_RATE_LIMIT_SEC: int = 5
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
