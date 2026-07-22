"""GET /patients, POST /patients/reset"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query

from backend.app.schemas import PatientOut, ResetPatientsResponse
from backend.app.services import patient_service

router = APIRouter(prefix="/patients", tags=["patients"])


@router.get("", response_model=List[PatientOut])
def get_patients() -> List[PatientOut]:
    return [PatientOut(**p.to_dict()) for p in patient_service.list_patients()]


@router.post("/reset", response_model=ResetPatientsResponse)
def reset_patients(patient_id: Optional[int] = Query(default=None)) -> Dict[str, Any]:
    return patient_service.reset_patients(patient_id)
