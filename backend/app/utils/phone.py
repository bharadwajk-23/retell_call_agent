"""Small phone-number helpers shared across services/repositories."""

import re


def normalize_phone(phone: str) -> str:
    """Strip whitespace so phone numbers compare reliably (E.164 recommended on input)."""
    return re.sub(r"\s+", "", (phone or "").strip())
