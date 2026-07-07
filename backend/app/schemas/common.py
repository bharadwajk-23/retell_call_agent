"""Shared response/error schemas used across routers."""

from typing import Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str


class HealthResponse(BaseModel):
    status: str
    retell_mock_calls: bool
    from_number_configured: bool


class ReadinessResponse(BaseModel):
    status: str
    reason: Optional[str] = None
