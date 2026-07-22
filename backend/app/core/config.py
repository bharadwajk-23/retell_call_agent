"""
Centralized application settings and filesystem paths, populated from
environment variables.

Nothing in this project should read `os.environ` directly outside this
module — every other layer depends on `get_settings()`.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BACKEND_DIR / "app" / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Runtime ---
    HOST: str = "0.0.0.0"
    PORT: int = 8006
    LOG_LEVEL: str = "INFO"

    # --- CORS ---
    # Comma-separated list of allowed origins (local frontend dev server).
    CORS_ORIGINS: str = "http://localhost:8005"

    # --- Retell AI ---
    RETELL_API_KEY: str = ""
    RETELL_AGENT_ID: str = ""
    RETELL_FROM_NUMBER: str = ""
    # Verify the `x-retell-signature` header on inbound webhooks using
    # RETELL_API_KEY as the shared secret (see retell.lib.webhook_auth).
    # Off by default: confirm the signing header name in the Retell
    # dashboard/docs for your account before enabling it.
    RETELL_WEBHOOK_VERIFY: bool = False

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


@lru_cache
def get_settings() -> Settings:
    return Settings()


def provider_details_path() -> Path:
    settings = get_settings()
    if settings.PROVIDER_DETAILS_PATH:
        return Path(settings.PROVIDER_DETAILS_PATH)
    return DATA_DIR / "provider_details.json"
