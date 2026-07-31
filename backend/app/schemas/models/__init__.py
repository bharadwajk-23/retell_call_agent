"""Domain dataclasses, kept separate from the API schemas in app/schemas/api_req_res/."""

from backend.app.schemas.models.appointment import Appointment
from backend.app.schemas.models.call import ActiveCall, CallLogEntry
from backend.app.schemas.models.patient import Patient

__all__ = ["Patient", "ActiveCall", "CallLogEntry", "Appointment"]
