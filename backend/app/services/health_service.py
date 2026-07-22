"""Business logic for liveness/readiness checks."""

from backend.app.core.config import get_settings
from backend.app.schemas.common import ReadinessResponse


def check_readiness() -> ReadinessResponse:
    settings = get_settings()
    if not settings.RETELL_FROM_NUMBER:
        return ReadinessResponse(status="not_ready", reason="RETELL_FROM_NUMBER is not configured")
    return ReadinessResponse(status="ready")
