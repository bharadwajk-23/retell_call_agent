"""GET /providers/availability"""

from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, Query

from backend.app.schemas.api_req_res import ProviderAvailability, ProvidersAvailabilityResponse
from backend.app.services import provider_service

router = APIRouter(prefix="/providers", tags=["providers"])


@router.get("/availability", response_model=Union[ProviderAvailability, ProvidersAvailabilityResponse])
def provider_availability(
    provider_name: Optional[str] = Query(
        None, description="Filter to one provider; omit for all provider records"
    ),
) -> Dict[str, Any]:
    """Retell custom function: list free slots (0=free, 1=booked) for a provider."""
    return provider_service.get_availability(provider_name)
