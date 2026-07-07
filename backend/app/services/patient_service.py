"""Business logic for patient listing and demo reset."""

from typing import List, Optional

from app.models.patient import Patient
from app.repositories.active_call_repository import active_call_repository
from app.repositories.appointment_repository import appointment_repository
from app.repositories.patient_repository import patient_repository
from app.services.call_service import cleanup_active_calls


def list_patients() -> List[Patient]:
    cleanup_active_calls()
    return patient_repository.list_all()


def reset_patients(patient_id: Optional[int] = None) -> dict:
    patient_repository.reset(patient_id)
    if patient_id is None:
        active_call_repository.clear()
        appointment_repository.clear()
    return {
        "status": "reset",
        "patient_id": patient_id,
        "reset_all": patient_id is None,
    }
