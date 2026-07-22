"""Small, dependency-light helpers shared across services/repositories."""

from backend.app.utils.json_files import load_json_file
from backend.app.utils.phone import normalize_phone

__all__ = [
    "load_json_file",
    "normalize_phone",
]
