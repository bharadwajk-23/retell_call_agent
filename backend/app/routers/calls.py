"""POST /calls/start, POST /calls/make, GET /calls/status, GET /calls/transcripts"""

from typing import Any, Dict

from fastapi import APIRouter, Query

from backend.app.schemas.call import (
    ActiveCallStatus,
    CallResponse,
    MakeCallRequest,
    StartCallRequest,
    TranscriptsResponse,
)
from backend.app.services import call_service

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/start", response_model=CallResponse)
def start_call(body: StartCallRequest) -> Dict[str, Any]:
    """Start an outbound call by patient id — used by the dashboard's Start Call button."""
    return call_service.start_call(body.patient_id)


@router.post("/make", response_model=CallResponse)
def make_call(body: MakeCallRequest) -> Dict[str, Any]:
    """Start an outbound call by phone number (alternate entrypoint)."""
    return call_service.make_call(body.phone)


@router.get("/status", response_model=ActiveCallStatus)
def call_status(phone: str = Query(..., description="Patient phone number")) -> Dict[str, Any]:
    return call_service.get_call_status(phone)


@router.get("/transcripts", response_model=TranscriptsResponse)
def transcripts() -> Dict[str, Any]:
    return call_service.list_transcripts()
