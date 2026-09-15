from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ---------- App ----------
    APP_NAME: str = "Algerian Digital ID"
    DEBUG: bool = False

    # ---------- Security ----------
    SECRET_KEY: str = "change-me-in-production-min-32-chars!!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # ---------- Redis ----------
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 50
    REDIS_SOCKET_TIMEOUT: float = 2.0

    # ---------- Revocation policy ----------
    REVOCATION_FAIL_CLOSED: bool = False
    REFRESH_ROTATION_ENABLED: bool = True
    REFRESH_REUSE_GRACE_SECONDS: int = 30

    # ---------- Database ----------
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
