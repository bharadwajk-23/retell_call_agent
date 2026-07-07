"""Liveness / readiness endpoints for load balancers and container orchestrators."""

from fastapi import APIRouter

from app.config.settings import get_settings
from app.schemas.common import HealthResponse, ReadinessResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    settings = get_settings()
    return HealthResponse(
        status="ok",
        retell_mock_calls=settings.RETELL_MOCK_CALLS,
        from_number_configured=bool(settings.RETELL_FROM_NUMBER),
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check():
    settings = get_settings()
    if not settings.RETELL_MOCK_CALLS and not settings.RETELL_FROM_NUMBER:
        return ReadinessResponse(status="not_ready", reason="RETELL_FROM_NUMBER is not configured")
    return ReadinessResponse(status="ready")
