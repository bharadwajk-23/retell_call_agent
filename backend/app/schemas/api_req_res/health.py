"""Schemas for the health/readiness endpoints (mirrors services/health_service.py)."""

from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    from_number_configured: bool


class ReadinessResponse(BaseModel):
    status: str
    reason: Optional[str] = None
