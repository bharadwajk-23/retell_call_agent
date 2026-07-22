"""Domain dataclasses, kept separate from the API schemas in app/schemas/."""

from backend.app.models.appointment import Appointment
from backend.app.models.call import ActiveCall, CallLogEntry
from backend.app.models.patient import Patient

__all__ = ["Patient", "ActiveCall", "CallLogEntry", "Appointment"]
