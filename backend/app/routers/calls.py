"""POST /api/calls/start, POST /api/calls/make, GET /api/calls/status, GET /api/calls/transcripts"""

from fastapi import APIRouter, Query

from app.repositories.call_log_repository import call_log_repository
from app.schemas.call import (
    ActiveCallStatus,
    CallResponse,
    MakeCallRequest,
    StartCallRequest,
    TranscriptsResponse,
)
from app.services import call_service

router = APIRouter(prefix="/api/calls", tags=["calls"])


@router.post("/start", response_model=CallResponse)
async def start_call(body: StartCallRequest):
    """Start an outbound call by patient id — used by the dashboard's Start Call button."""
    return call_service.start_call(body.patient_id)


@router.post("/make", response_model=CallResponse)
async def make_call(body: MakeCallRequest):
    """Start an outbound call by phone number (alternate entrypoint)."""
    return call_service.make_call(body.phone)


@router.get("/status", response_model=ActiveCallStatus)
async def call_status(phone: str = Query(..., description="Patient phone number")):
    return call_service.get_call_status(phone)


@router.get("/transcripts", response_model=TranscriptsResponse)
async def transcripts():
    return {"transcripts": [entry.to_dict() for entry in call_log_repository.list_all()]}
