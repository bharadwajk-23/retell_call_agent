"""Business logic for processing inbound Retell webhook events."""

from datetime import datetime
from typing import Any, Dict

from fastapi import HTTPException

from backend.app.core.config import get_settings
from backend.app.core.logging import get_logger
from backend.app.core.security import verify_retell_signature
from backend.app.repositories.active_call_repository import active_call_repository
from backend.app.repositories.appointment_repository import appointment_repository
from backend.app.repositories.call_log_repository import call_log_repository
from backend.app.repositories.patient_repository import patient_repository

logger = get_logger(__name__)


def verify_signature(body: bytes, signature: str) -> None:
    """Enforce the `x-retell-signature` check when RETELL_WEBHOOK_VERIFY is on.

    No-op if verification is disabled. Raises 401 on a missing/invalid
    signature so the router never receives an unverified webhook.
    """
    settings = get_settings()
    if not settings.RETELL_WEBHOOK_VERIFY:
        return
    if not verify_retell_signature(body, settings.RETELL_API_KEY, signature):
        logger.warning("Rejected Retell webhook: missing or invalid x-retell-signature")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


def handle_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    event = payload.get("event")
    call_id = payload.get("call_id")
    data = payload.get("data", payload)

    log_payload: Dict[str, Any] = {"call_id": call_id, "data": data}
    if isinstance(data, dict):
        transcript = data.get("transcript") or data.get("transcript_text")
        if transcript:
            log_payload["transcript"] = transcript

    call_log_repository.append(event=event or "unknown", timestamp=datetime.now().isoformat(), payload=log_payload)

    if event == "call_ended" and call_id:
        phone = active_call_repository.find_by_call_id(call_id)
        if phone:
            call = active_call_repository.get(phone)
            appointment_booked = None
            if call:
                call.status = "completed"
                call.ended_at = datetime.now().isoformat()

                appointment_booked = False
                if call.patient_id is not None and call.started_at:
                    appointment_booked = appointment_repository.booked_after(call.started_at)

                if not appointment_booked and call.patient_id is not None:
                    patient_repository.set_booking_status(call.patient_id, "not booked")

            active_call_repository.remove(phone)
            logger.info("Call ended: call_id=%s appointment_booked=%s", call_id, appointment_booked)

    return {"status": "received"}
