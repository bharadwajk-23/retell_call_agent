from typing import Optional

from pydantic import BaseModel


class PatientOut(BaseModel):
    id: int
    patient_name: str
    phone: str
    dob: str
    provider_name: str
    exercise_missed_days: int
    booking_status: str
    appointment_id: Optional[str] = None


class ResetPatientsResponse(BaseModel):
    status: str
    patient_id: Optional[int] = None
    reset_all: bool
