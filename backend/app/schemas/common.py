"""Shared response/error schemas used across routers."""

from typing import Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    from_number_configured: bool


class ReadinessResponse(BaseModel):
    status: str
    reason: Optional[str] = None
