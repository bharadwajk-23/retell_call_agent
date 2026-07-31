from typing import List

from pydantic import BaseModel


class FreeSlot(BaseModel):
    weekday: str
    time: str


class ProviderAvailability(BaseModel):
    provider_name: str
    found: bool
    free_slots: List[FreeSlot]
    message: str


class ProvidersAvailabilityResponse(BaseModel):
    providers: List[ProviderAvailability]
