"""
Centralized application settings and filesystem paths, sourced directly from
environment variables via `os.getenv`.

Nothing in this project should call `os.environ`/`os.getenv` directly
outside this module — every other layer depends on `get_settings()`.
Settings are split into one class per concern (server, CORS, Retell,
business rules) and composed into a single `Settings` object via multiple
inheritance so callers keep using flat attribute access (e.g.
`settings.RETELL_API_KEY`).
"""

import os
from functools import lru_cache
from pathlib import Path
from typing import List

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
DATA_DIR = BACKEND_DIR / "app" / "data"
INPUT_DIR = DATA_DIR / "input"

# Populates os.environ from the project-root .env (without overriding real
# process environment variables that are already set) so every os.getenv()
# call below sees it, regardless of import order.
load_dotenv(PROJECT_ROOT / ".env")


def _getenv_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _getenv_list(name: str, default: List[str]) -> List[str]:
    value = os.getenv(name)
    if value is None:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


class ServerSettings:
    """Uvicorn bind address and logging level."""

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8006"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


class CORSSettings:
    """Allowed frontend origins for CORSMiddleware."""

    # Comma-separated list of allowed origins (local frontend dev server).
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:8005")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


class RetellSettings:
    """Retell AI credentials and webhook security."""

    RETELL_API_KEY: str = os.getenv("RETELL_API_KEY", "")
    RETELL_AGENT_ID: str = os.getenv("RETELL_AGENT_ID", "")
    RETELL_FROM_NUMBER: str = os.getenv("RETELL_FROM_NUMBER", "")
    # Verify the `x-retell-signature` header on inbound webhooks using
    # RETELL_API_KEY as the shared secret (see retell.lib.webhook_auth).
    # Off by default: confirm the signing header name in the Retell
    # dashboard/docs for your account before enabling it.
    RETELL_WEBHOOK_VERIFY: bool = _getenv_bool("RETELL_WEBHOOK_VERIFY", False)


class BusinessRuleSettings:
    """Reference-data overrides and call-lifecycle tuning (previously magic numbers)."""

    PROVIDER_DETAILS_PATH: str = os.getenv("PROVIDER_DETAILS_PATH", "")  # resolved to app/data/input/provider_details.json if blank
    CALL_STALE_SECONDS: int = int(os.getenv("CALL_STALE_SECONDS", "20"))
    SLOT_HOUR_LABELS: List[str] = _getenv_list(
        "SLOT_HOUR_LABELS",
        ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00"],
    )


class Settings(ServerSettings, CORSSettings, RetellSettings, BusinessRuleSettings):
    """Combines every settings group above into the one object `get_settings()` returns."""


@lru_cache
def get_settings() -> Settings:
    return Settings()


def provider_details_path() -> Path:
    settings = get_settings()
    if settings.PROVIDER_DETAILS_PATH:
        return Path(settings.PROVIDER_DETAILS_PATH)
    return INPUT_DIR / "provider_details.json"
