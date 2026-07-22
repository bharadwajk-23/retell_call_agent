"""Liveness / readiness endpoints for load balancers and container orchestrators."""

from fastapi import APIRouter

from backend.app.core.config import get_settings
from backend.app.schemas.common import HealthResponse, ReadinessResponse
from backend.app.services import health_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        from_number_configured=bool(settings.RETELL_FROM_NUMBER),
    )


@router.get("/ready", response_model=ReadinessResponse)
def readiness_check() -> ReadinessResponse:
    return health_service.check_readiness()
