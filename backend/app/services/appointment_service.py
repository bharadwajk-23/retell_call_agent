"""Business logic for creating and listing appointments."""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.appointment import Appointment
from app.repositories.appointment_repository import appointment_repository
from app.repositories.call_log_repository import call_log_repository
from app.repositories.patient_repository import patient_repository
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


def book_appointment(
    patient_name: str,
    provider_name: str,
    phone: Optional[str],
    slot_weekday: Optional[str],
    slot_time: Optional[str],
    notes: Optional[str],
) -> Dict[str, Any]:
    record = Appointment(
        appointment_id=f"APT{uuid.uuid4().hex[:8].upper()}",
        patient_name=patient_name,
        provider_name=provider_name,
        phone=phone,
        slot_weekday=slot_weekday,
        slot_time=slot_time,
        notes=notes,
        booked_at=datetime.now().isoformat(),
    )
    appointment_repository.add(record)

    call_log_repository.append(
        event="appointment_booked",
        timestamp=record.booked_at,
        payload={
            "appointment_id": record.appointment_id,
            "patient_name": patient_name,
            "provider_name": provider_name,
            "slot_weekday": slot_weekday,
            "slot_time": slot_time,
        },
    )

    patient_repository.mark_booked(record.appointment_id, phone, patient_name)

    logger.info(
        "Appointment booked: id=%s patient=%s provider=%s slot=%s %s",
        record.appointment_id,
        patient_name,
        provider_name,
        slot_weekday,
        slot_time,
    )

    return {
        "status": "success",
        "appointment_id": record.appointment_id,
        "message": (
            f"Appointment confirmed for {patient_name} with {provider_name} "
            f"on {slot_weekday} at {slot_time}"
        ),
        "appointment": record.to_dict(),
    }


def list_appointments() -> List[Dict[str, Any]]:
    return [a.to_dict() for a in appointment_repository.list_all()]
