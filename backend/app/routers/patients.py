"""GET /api/patients, POST /api/patients/reset"""

from typing import List, Optional

from fastapi import APIRouter, Query

from app.schemas.patient import PatientOut, ResetPatientsResponse
from app.services import patient_service

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("", response_model=List[PatientOut])
async def get_patients():
    return [PatientOut(**p.to_dict()) for p in patient_service.list_patients()]


@router.post("/reset", response_model=ResetPatientsResponse)
async def reset_patients(patient_id: Optional[int] = Query(default=None)):
    return patient_service.reset_patients(patient_id)
