"""Configuration definition."""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings", "settings"]

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class EnvSettingsOptions(Enum):
    production = "production"
    staging = "staging"
    development = "dev"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        case_sensitive=False,
        extra="ignore",
    )

    # Project Configuration
    ENV_SETTING: EnvSettingsOptions = Field(
        "production",
        examples=["production", "staging", "dev"],
    )

    # Database Configuration
    POSTGRES_HOST: str = Field()
    POSTGRES_PORT: int = Field()
    POSTGRES_USER: str = Field()
    POSTGRES_PASSWORD: str = Field()
    POSTGRES_DBNAME: str = Field()

    # Database Connection Pooling Configuration
    DB_POOL_SIZE: int = Field(default=20, description="Number of connections to maintain in the pool")
    DB_MAX_OVERFLOW: int = Field(default=30, description="Additional connections beyond pool_size")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Timeout for getting connection from pool (seconds)")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Recycle connections after N seconds")
    DB_POOL_PRE_PING: bool = Field(default=True, description="Validate connections before use")
    DB_ECHO: bool = Field(default=False, description="Enable SQL query logging")


settings = Settings()
