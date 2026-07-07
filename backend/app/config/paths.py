"""Filesystem path helpers, kept separate from Settings so tests can override easily."""

from pathlib import Path

from app.config.settings import get_settings

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BACKEND_DIR / "app" / "data"


def provider_details_path() -> Path:
    settings = get_settings()
    if settings.PROVIDER_DETAILS_PATH:
        return Path(settings.PROVIDER_DETAILS_PATH)
    return DATA_DIR / "provider_details.json"
