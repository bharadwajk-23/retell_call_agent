"""Business logic for processing inbound Retell webhook events."""

from datetime import datetime
from typing import Any, Dict

from app.repositories.active_call_repository import active_call_repository
from app.repositories.appointment_repository import appointment_repository
from app.repositories.call_log_repository import call_log_repository
from app.repositories.patient_repository import patient_repository
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


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
            if call:
                call.status = "completed"
                call.ended_at = datetime.now().isoformat()

                appointment_booked = False
                if call.patient_id is not None and call.started_at:
                    appointment_booked = appointment_repository.booked_after(call.started_at)

                if not appointment_booked and call.patient_id is not None:
                    patient_repository.set_booking_status(call.patient_id, "not booked")

            active_call_repository.remove(phone)
            logger.info("Call ended: call_id=%s appointment_booked=%s", call_id, appointment_booked if phone else None)

    return {"status": "received"}
