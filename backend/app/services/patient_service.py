"""Business logic for patient listing and demo reset."""

from typing import Any, Dict, List, Optional

from backend.app.schemas.models import Patient
from backend.app.repositories import active_call_repository, appointment_repository, patient_repository
from backend.app.services.call_service import cleanup_active_calls


def list_patients() -> List[Patient]:
    cleanup_active_calls()
    return patient_repository.list_all()


def reset_patients(patient_id: Optional[int] = None) -> Dict[str, Any]:
    patient_repository.reset(patient_id)
    if patient_id is None:
        active_call_repository.clear()
        appointment_repository.clear()
    return {
        "status": "reset",
        "patient_id": patient_id,
        "reset_all": patient_id is None,
    }
