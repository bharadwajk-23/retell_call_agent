"""POST/GET /appointments, POST /appointments/book"""

from typing import Any, Dict, List

from fastapi import APIRouter

from backend.app.schemas.appointment import (
    AppointmentOut,
    AppointmentRequest,
    BookAppointmentRequest,
    BookAppointmentResponse,
)
from backend.app.services import appointment_service

router = APIRouter(prefix="/appointments", tags=["appointments"])


@router.post("", response_model=BookAppointmentResponse)
def create_appointment(appointment: AppointmentRequest) -> Dict[str, Any]:
    return appointment_service.book_appointment(
        patient_name=appointment.patient_name,
        provider_name=appointment.provider_name,
        phone=appointment.phone,
        slot_weekday=appointment.slot_weekday,
        slot_time=appointment.slot_time,
        notes=appointment.notes,
    )


@router.post("/book", response_model=BookAppointmentResponse)
def book_appointment(body: BookAppointmentRequest) -> Dict[str, Any]:
    """Retell custom function: books a slot the patient agreed to during the call."""
    return appointment_service.book_appointment(
        patient_name=body.patient_name,
        provider_name=body.provider_name,
        phone=body.phone,
        slot_weekday=body.slot_weekday,
        slot_time=body.slot_time,
        notes=body.notes,
    )


@router.get("", response_model=List[AppointmentOut])
def list_appointments() -> List[Dict[str, Any]]:
    return appointment_service.list_appointments()
