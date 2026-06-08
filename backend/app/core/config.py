"""Application configuration loaded from environment variables."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings object.

    Defaults are chosen so the platform runs out-of-the-box with SQLite for
    local development, while ``DATABASE_URL`` can point at PostgreSQL in
    Docker / production.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "Accessible Climate Data Integration Platform"
    API_V1_PREFIX: str = "/api"

    # Database. Example PostgreSQL URL:
    #   postgresql+psycopg2://climate:climate@db:5432/climate
    DATABASE_URL: str = "sqlite:///./climate.db"

    # Security
    SECRET_KEY: str = "change-me-in-production-please-use-a-long-random-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    # Default seeded admin account
    FIRST_ADMIN_USERNAME: str = "admin"
    FIRST_ADMIN_PASSWORD: str = "admin123"
    FIRST_ADMIN_EMAIL: str = "admin@climate.example.com"

    # CORS
    CORS_ORIGINS: str = "*"

    # Auto-run ETL seed on startup if DB empty
    SEED_ON_STARTUP: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
