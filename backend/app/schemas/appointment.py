from typing import Optional

from pydantic import BaseModel

from backend.app.core.constants import DEFAULT_PROVIDER_NAME, DEFAULT_SLOT_TIME, DEFAULT_SLOT_WEEKDAY


class AppointmentRequest(BaseModel):
    """Generic appointment-creation body (used by /appointments)."""

    patient_name: str
    provider_name: str
    phone: Optional[str] = None
    slot_weekday: Optional[str] = None
    slot_time: Optional[str] = None
    notes: Optional[str] = None


class BookAppointmentRequest(BaseModel):
    """Body shape for the Retell custom function that books a slot.

    Defaults intentionally mirror the original implementation so the voice
    agent's existing custom-function configuration keeps working unchanged.
    """

    patient_name: str = ""
    provider_name: str = DEFAULT_PROVIDER_NAME
    phone: Optional[str] = None
    slot_weekday: str = DEFAULT_SLOT_WEEKDAY
    slot_time: str = DEFAULT_SLOT_TIME
    notes: Optional[str] = None


class AppointmentOut(BaseModel):
    appointment_id: str
    patient_name: str
    provider_name: str
    phone: Optional[str] = None
    slot_weekday: Optional[str] = None
    slot_time: Optional[str] = None
    notes: Optional[str] = None
    booked_at: str


class BookAppointmentResponse(BaseModel):
    status: str
    appointment_id: str
    message: str
    appointment: AppointmentOut
