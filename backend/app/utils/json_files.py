"""Read-only helpers for the small amount of reference data kept as JSON on disk."""

import json
from pathlib import Path
from typing import Any

from backend.app.core import get_logger

logger = get_logger(__name__)


def load_json_file(file_path: Path) -> Any:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning("JSON file not found: %s", file_path)
        return []
    except json.JSONDecodeError:
        logger.error("JSON file is not valid JSON: %s", file_path)
        return []
