"""Generic helper for reading a field off either a dict or an object.

Useful for SDK responses that vary in shape (dict in some cases, a typed
object in others) depending on the call path.
"""

from typing import Any


def get_field(source: Any, name: str, default: Any = None) -> Any:
    if isinstance(source, dict):
        return source.get(name, default)
    return getattr(source, name, default)
