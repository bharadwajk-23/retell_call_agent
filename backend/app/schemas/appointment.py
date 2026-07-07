from typing import Optional

from pydantic import BaseModel


class AppointmentRequest(BaseModel):
    """Generic appointment-creation body (used by /api/appointments)."""

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
    provider_name: str = "Bharadwaj"
    phone: Optional[str] = None
    slot_weekday: str = "Monday"
    slot_time: str = "09:00 am"
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
