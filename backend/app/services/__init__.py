"""Business logic, one module per resource: patient, call, health, provider, appointment, webhook.

Every public function/class in each module is re-exported here, so callers
can do `from backend.app.services import book_appointment` without knowing
which submodule it lives in. The submodules themselves (e.g.
`appointment_service`) are re-exported too, for call sites that prefer the
module-qualified form.
"""


from backend.app.services.appointment_service import book_appointment, list_appointments
from backend.app.services.call_service import (
    call_is_inactive,
    cleanup_active_calls,
    execute_outbound_call,
    get_call_status,
    list_transcripts,
    make_call,
    require_from_number,
    start_call,
)
from backend.app.services.client_services import RetellClient, retell_client
from backend.app.services.health_service import check_readiness
from backend.app.services.patient_service import list_patients, reset_patients
from backend.app.services.provider_service import free_slots_for_provider, get_availability
from backend.app.services.security_service import verify_retell_signature
from backend.app.services.webhook_service import handle_webhook, verify_signature

__all__ = [
    "appointment_service",
    "call_service",
    "health_service",
    "patient_service",
    "provider_service",
    "security_service",
    "webhook_service",
    "RetellClient",
    "retell_client",
    "book_appointment",
    "list_appointments",
    "call_is_inactive",
    "cleanup_active_calls",
    "execute_outbound_call",
    "get_call_status",
    "list_transcripts",
    "make_call",
    "require_from_number",
    "start_call",
    "check_readiness",
    "list_patients",
    "reset_patients",
    "free_slots_for_provider",
    "get_availability",
    "verify_retell_signature",
    "handle_webhook",
    "verify_signature",
]
