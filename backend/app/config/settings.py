"""
Centralized application settings, populated from environment variables.

Nothing in this project should read `os.environ` directly outside this
module — every other layer depends on `get_settings()`.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Runtime ---
    ENV: str = "development"  # "development" | "production"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # --- CORS ---
    # Comma-separated list of allowed origins, e.g. "http://localhost:5173,https://app.example.com"
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Retell AI ---
    RETELL_API_KEY: str = ""
    RETELL_AGENT_ID: str = ""
    RETELL_FROM_NUMBER: str = ""
    RETELL_MOCK_CALLS: bool = False

    # --- Reference data ---
    PROVIDER_DETAILS_PATH: str = ""  # resolved to app/data/provider_details.json if blank

    # --- Business rules (previously magic numbers) ---
    CALL_STALE_SECONDS: int = 20
    SLOT_HOUR_LABELS: List[str] = [
        "09:00",
        "10:00",
        "11:00",
        "12:00",
        "13:00",
        "14:00",
        "15:00",
        "16:00",
        "17:00",
        "18:00",
    ]

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.ENV.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
