from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings sourced from env vars or .env file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="URLS_",  # Matches URLS_DATABASE_URL, URLS_BASE_URL, etc.
        case_sensitive=False
    )

    app_name: str = "URL Shortener"
    database_url: str = Field(
        default="sqlite:///./url_shortener.db",
    )
    base_url: AnyHttpUrl = Field(default="http://localhost:8000")
    code_length: int = Field(default=6, ge=4, le=16)


@lru_cache
def get_settings() -> Settings:
    return Settings()
