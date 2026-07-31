"""Small, dependency-light helpers shared across services/repositories.

Every public function/class from each utility module is re-exported here,
so callers can do `from backend.app.utils import load_json_file` without
knowing which submodule it lives in.
"""

from backend.app.utils.error_handlers import register_exception_handlers
from backend.app.utils.json_files import load_json_file
from backend.app.utils.phone import normalize_phone
from backend.app.utils.request_logging import RequestLoggingMiddleware
from backend.app.utils.response_parsing import get_field
from backend.app.utils.time_utils import is_stale

__all__ = [
    "load_json_file",
    "normalize_phone",
    "get_field",
    "is_stale",
    "register_exception_handlers",
    "RequestLoggingMiddleware",
]
