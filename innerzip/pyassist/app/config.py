import os
from pydantic import BaseModel

from typing import Optional, List

class Settings(BaseModel):
    APP_NAME: str = "PyAssist"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pyassist-insecure-dev-secret-key-change-in-prod-32bytes")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./pyassist.db")
    SESSION_COOKIE_NAME: str = "pyassist_session"
    CSRF_COOKIE_NAME: str = "pyassist_csrf"
    SESSION_MAX_AGE_SECONDS: int = 60 * 60 * 24 * 7  # 7 days
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() in ("true", "1", "yes")
    COOKIE_SAMESITE: str = "lax"
    MAX_QUESTION_LENGTH: int = 4000
    RATE_LIMIT_LOGIN: str = "10/minute"
    RATE_LIMIT_REGISTER: str = "5/minute"
    RATE_LIMIT_CHAT: str = "30/minute"

    # Gemini AI configuration
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    GEMINI_PRIMARY_MODEL: str = os.getenv("GEMINI_PRIMARY_MODEL", "gemini-3.1-flash-lite")
    GEMINI_FALLBACK_MODELS: List[str] = ["gemini-flash-latest", "gemini-3.8-flash"]
    GEMINI_TIMEOUT_SECONDS: int = int(os.getenv("GEMINI_TIMEOUT_SECONDS", "30"))

settings = Settings()
