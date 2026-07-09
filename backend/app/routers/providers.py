"""GET /api/providers/availability"""

from typing import Optional

from fastapi import APIRouter, Query

from app.services import provider_service

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/availability")
async def provider_availability(
    provider_name: Optional[str] = Query(
        None, description="Filter to one provider; omit for all provider records"
    ),
):
    """Retell custom function: list free slots (0=free, 1=booked) for a provider."""
    return provider_service.get_availability(provider_name)
