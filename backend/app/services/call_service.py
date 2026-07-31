"""Business logic for placing and tracking outbound Retell calls."""

import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException

from backend.app.core import ACTIVE_CALL_STATUSES, DETAILS_TERMINAL_STATUSES, TERMINAL_CALL_STATUSES, get_logger, get_settings
from backend.app.services.client_services import retell_client
from backend.app.schemas.models import ActiveCall, Patient
from backend.app.repositories import active_call_repository, call_log_repository, patient_repository
from backend.app.utils import get_field, is_stale, normalize_phone

logger = get_logger(__name__)


def require_from_number() -> str:
    settings = get_settings()
    if not settings.RETELL_FROM_NUMBER:
        raise HTTPException(
            status_code=500,
            detail="RETELL_FROM_NUMBER is not configured (your Telnyx/Twilio number in E.164)",
        )
    return settings.RETELL_FROM_NUMBER


def execute_outbound_call(patient: Patient) -> Dict[str, Any]:
    settings = get_settings()
    phone = normalize_phone(patient.phone)
    from_number = require_from_number()

    call_response = retell_client.trigger_outbound_call(
        phone_number=phone,
        from_number=from_number,
        patient_name=patient.patient_name,
        provider_name=patient.provider_name,
        exercise_missed_days=patient.exercise_missed_days,
        agent_id=settings.RETELL_AGENT_ID or None,
    )

    if not call_response:
        raise HTTPException(status_code=500, detail="Failed to trigger call")

    call_id = get_field(call_response, "call_id") or str(uuid.uuid4())
    started_at = datetime.now().isoformat()

    active_call_repository.set(
        phone,
        ActiveCall(
            call_id=call_id,
            status=get_field(call_response, "call_status") or "registered",
            started_at=started_at,
            phone=phone,
            patient_name=patient.patient_name,
            patient_id=patient.id,
        ),
    )

    call_log_repository.append(
        event="call_started",
        timestamp=started_at,
        payload={
            "call_id": call_id,
            "phone": phone,
            "patient_id": patient.id,
            "patient_name": patient.patient_name,
        },
    )

    logger.info("Call started: patient_id=%s call_id=%s", patient.id, call_id)

    return {
        "status": "call generated",
        "call_id": call_id,
        "patient_id": patient.id,
        "patient_name": patient.patient_name,
        "provider_name": patient.provider_name,
        "doctor_name": patient.provider_name,
        "exercise_missed_days": patient.exercise_missed_days,
        "phone": phone,
    }


def start_call(patient_id: int) -> Dict[str, Any]:
    patient = patient_repository.get_by_id(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient_repository.set_booking_status(patient_id, "in progress")
    try:
        return execute_outbound_call(patient)
    except Exception:
        patient_repository.set_booking_status(patient_id, "not booked")
        raise


def make_call(phone: str) -> Dict[str, Any]:
    patient = patient_repository.get_by_phone(phone)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found for phone number")
    return execute_outbound_call(patient)


def get_call_status(phone: str) -> Dict[str, Any]:
    key = normalize_phone(phone)
    call = active_call_repository.get(key)
    if not call:
        raise HTTPException(status_code=404, detail="No active call found")
    return call.to_dict()


def call_is_inactive(call: ActiveCall) -> bool:
    if call.status in TERMINAL_CALL_STATUSES:
        return True

    details = retell_client.get_call_details(call.call_id) if call.call_id else None
    if details:
        details_status = get_field(details, "call_status")
        if details_status in ACTIVE_CALL_STATUSES:
            return False
        if details_status in DETAILS_TERMINAL_STATUSES:
            return True

    settings = get_settings()
    return is_stale(call.started_at, settings.CALL_STALE_SECONDS)


def cleanup_active_calls() -> None:
    for call in active_call_repository.all_items():
        if call_is_inactive(call):
            if call.patient_id is not None:
                patient = patient_repository.get_by_id(call.patient_id)
                if patient and patient.booking_status == "in progress":
                    patient_repository.set_booking_status(call.patient_id, "not booked")
            active_call_repository.remove(call.phone)


def list_transcripts() -> Dict[str, Any]:
    return {"transcripts": [entry.to_dict() for entry in call_log_repository.list_all()]}
