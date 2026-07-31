"""Shared error schema used across routers."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
