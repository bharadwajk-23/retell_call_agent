"""Business logic for placing and tracking outbound Retell calls."""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException

from backend.app.clients.retell_client import retell_client
from backend.app.core.config import get_settings
from backend.app.core.constants import ACTIVE_CALL_STATUSES, DETAILS_TERMINAL_STATUSES, TERMINAL_CALL_STATUSES
from backend.app.core.logging import get_logger
from backend.app.models.call import ActiveCall
from backend.app.models.patient import Patient
from backend.app.repositories.active_call_repository import active_call_repository
from backend.app.repositories.call_log_repository import call_log_repository
from backend.app.repositories.patient_repository import patient_repository
from backend.app.utils.phone import normalize_phone

logger = get_logger(__name__)


def _require_from_number() -> str:
    settings = get_settings()
    if not settings.RETELL_FROM_NUMBER:
        raise HTTPException(
            status_code=500,
            detail="RETELL_FROM_NUMBER is not configured (your Telnyx/Twilio number in E.164)",
        )
    return settings.RETELL_FROM_NUMBER


def _call_id_from_response(call_response: Any) -> str:
    cid = getattr(call_response, "call_id", None)
    if cid is None and isinstance(call_response, dict):
        cid = call_response.get("call_id")
    if cid is not None:
        return cid
    import uuid

    return str(uuid.uuid4())


def _status_from_response(call_response: Any) -> Optional[str]:
    if isinstance(call_response, dict):
        return call_response.get("call_status")
    return getattr(call_response, "call_status", None)


def _execute_outbound_call(patient: Patient) -> Dict[str, Any]:
    settings = get_settings()
    phone = normalize_phone(patient.phone)
    from_number = _require_from_number()

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

    call_id = _call_id_from_response(call_response)
    started_at = datetime.now().isoformat()

    active_call_repository.set(
        phone,
        ActiveCall(
            call_id=call_id,
            status=_status_from_response(call_response) or "registered",
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
        return _execute_outbound_call(patient)
    except Exception:
        patient_repository.set_booking_status(patient_id, "not booked")
        raise


def make_call(phone: str) -> Dict[str, Any]:
    patient = patient_repository.get_by_phone(phone)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found for phone number")
    return _execute_outbound_call(patient)


def get_call_status(phone: str) -> Dict[str, Any]:
    key = normalize_phone(phone)
    call = active_call_repository.get(key)
    if not call:
        raise HTTPException(status_code=404, detail="No active call found")
    return call.to_dict()


def _call_is_stale(call: ActiveCall) -> bool:
    settings = get_settings()
    try:
        started_at = datetime.fromisoformat(call.started_at)
    except (TypeError, ValueError):
        return False
    return (datetime.now() - started_at).total_seconds() >= settings.CALL_STALE_SECONDS


def _call_is_inactive(call: ActiveCall) -> bool:
    if call.status in TERMINAL_CALL_STATUSES:
        return True

    details = retell_client.get_call_details(call.call_id) if call.call_id else None
    if details:
        details_status = (
            details.get("call_status") if isinstance(details, dict) else getattr(details, "call_status", None)
        )
        if details_status in ACTIVE_CALL_STATUSES:
            return False
        if details_status in DETAILS_TERMINAL_STATUSES:
            return True

    return _call_is_stale(call)


def cleanup_active_calls() -> None:
    for call in active_call_repository.all_items():
        if _call_is_inactive(call):
            if call.patient_id is not None:
                patient = patient_repository.get_by_id(call.patient_id)
                if patient and patient.booking_status == "in progress":
                    patient_repository.set_booking_status(call.patient_id, "not booked")
            active_call_repository.remove(call.phone)


def list_transcripts() -> Dict[str, Any]:
    return {"transcripts": [entry.to_dict() for entry in call_log_repository.list_all()]}
