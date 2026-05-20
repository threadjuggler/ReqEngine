"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic-settings model reading from .env or environment."""

    database_url: str = "postgresql+asyncpg://appuser:apppassword@localhost:5432/reqengine"
    redis_url: str = "redis://localhost:6379/0"
    uvicorn_workers: int = 4
    cors_origins: str = "*"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
