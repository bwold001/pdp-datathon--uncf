"""Application settings, resolved per environment.

APP_ENV picks the environment (development | staging | production). Settings are then
loaded from, in increasing priority:

    .env.<APP_ENV>          committed, non-secret defaults
    .env.<APP_ENV>.local    git-ignored, local secrets and overrides
    real environment vars   what a hosting platform injects

so the same code runs everywhere and only configuration changes.
"""

import os
from enum import StrEnum
from functools import lru_cache
from pathlib import Path

from measures.run_measures import DEFAULT_DATABASE
from pydantic_settings import BaseSettings, SettingsConfigDict

SERVER_ROOT = Path(__file__).resolve().parents[2]

# Swagger UI. Hidden in production; error responses point here otherwise.
DOCS_PATH = "/docs"


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


def _current_environment() -> Environment:
    return Environment(os.getenv("APP_ENV", Environment.DEVELOPMENT))


def _env_files(environment: Environment) -> tuple[Path, ...]:
    return (
        SERVER_ROOT / f".env.{environment}",
        SERVER_ROOT / f".env.{environment}.local",
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_env_files(_current_environment()),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_ENV: Environment = Environment.DEVELOPMENT
    PROJECT_NAME: str = "Playground API"
    VERSION: str = "0.1.0"
    API_V1_PREFIX: str = "/api/v1"

    # The synthetic SQLite extract `python -m api load` builds. A postgresql:// URL also works.
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DATABASE}"

    CORS_ORIGINS: list[str] = []

    # Provider keys stay server-side in .env.<APP_ENV>.local or the host secret store.
    OPENROUTER_API_KEY: str | None = None
    # Explicitly enabled for the local synthetic demo.
    UNCF_CHAT_ENABLED: bool = False
    UNCF_CHAT_MODEL: str = "openai/gpt-4.1"

    @property
    def chat_model(self) -> str:
        """Require a canonical OpenRouter ID without guessing legacy model mappings."""
        model = self.UNCF_CHAT_MODEL.strip()
        if "/" not in model or any(not part for part in model.split("/")):
            raise ValueError("UNCF_CHAT_MODEL must be a canonical OpenRouter model ID.")
        return model

    @property
    def is_development(self) -> bool:
        return self.APP_ENV is Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.APP_ENV is Environment.PRODUCTION

    @property
    def docs_path(self) -> str | None:
        """Where Swagger UI is served, or None in production, where it is turned off."""
        return None if self.is_production else DOCS_PATH


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
