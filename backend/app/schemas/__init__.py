"""Pydantic request/response models, one module per resource."""

from backend.app.schemas.appointment import (
    AppointmentOut,
    AppointmentRequest,
    BookAppointmentRequest,
    BookAppointmentResponse,
)
from backend.app.schemas.call import (
    ActiveCallStatus,
    CallResponse,
    MakeCallRequest,
    StartCallRequest,
    TranscriptsResponse,
)
from backend.app.schemas.common import ErrorResponse
from backend.app.schemas.health import HealthResponse, ReadinessResponse
from backend.app.schemas.patient import PatientOut, ResetPatientsResponse
from backend.app.schemas.provider import FreeSlot, ProviderAvailability, ProvidersAvailabilityResponse
from backend.app.schemas.webhook import RetellWebhookPayload, WebhookAck

__all__ = [
    "ErrorResponse",
    "HealthResponse",
    "ReadinessResponse",
    "PatientOut",
    "ResetPatientsResponse",
    "StartCallRequest",
    "MakeCallRequest",
    "CallResponse",
    "ActiveCallStatus",
    "TranscriptsResponse",
    "FreeSlot",
    "ProviderAvailability",
    "ProvidersAvailabilityResponse",
    "AppointmentRequest",
    "BookAppointmentRequest",
    "AppointmentOut",
    "BookAppointmentResponse",
    "RetellWebhookPayload",
    "WebhookAck",
]
