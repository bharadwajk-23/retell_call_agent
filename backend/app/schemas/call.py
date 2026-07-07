from typing import Optional

from pydantic import BaseModel, Field


class StartCallRequest(BaseModel):
    patient_id: int = Field(..., description="Patient id to call")


class MakeCallRequest(BaseModel):
    phone: str = Field(..., description="Patient phone number (E.164 recommended)")


class CallResponse(BaseModel):
    status: str
    call_id: str
    patient_id: Optional[int] = None
    patient_name: Optional[str] = None
    provider_name: Optional[str] = None
    doctor_name: Optional[str] = None
    exercise_missed_days: Optional[int] = None
    phone: str
    mock: bool


class ActiveCallStatus(BaseModel):
    call_id: str
    status: str
    started_at: str
    phone: str
    patient_name: Optional[str] = None
    patient_id: Optional[int] = None
    ended_at: Optional[str] = None


class TranscriptsResponse(BaseModel):
    transcripts: list
