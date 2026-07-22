"""Generic timestamp helpers."""

from datetime import datetime


def is_stale(timestamp: str, max_age_seconds: int) -> bool:
    """True if the ISO-format `timestamp` is older than `max_age_seconds`.

    False if `timestamp` can't be parsed, rather than raising.
    """
    try:
        parsed = datetime.fromisoformat(timestamp)
    except (TypeError, ValueError):
        return False
    return (datetime.now() - parsed).total_seconds() >= max_age_seconds
