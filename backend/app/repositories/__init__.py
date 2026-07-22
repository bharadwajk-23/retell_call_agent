"""In-memory data stores (singletons). No database — see each module's docstring."""

from backend.app.repositories.active_call_repository import active_call_repository
from backend.app.repositories.appointment_repository import appointment_repository
from backend.app.repositories.call_log_repository import call_log_repository
from backend.app.repositories.patient_repository import patient_repository
from backend.app.repositories.provider_repository import provider_repository

__all__ = [
    "patient_repository",
    "active_call_repository",
    "call_log_repository",
    "provider_repository",
    "appointment_repository",
]
