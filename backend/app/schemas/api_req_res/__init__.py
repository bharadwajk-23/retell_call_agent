"""Pydantic request/response models, one module per resource."""

from backend.app.schemas.api_req_res.appointment import (
    AppointmentBookingResponse,
    AppointmentResponse,
    CreateAppointmentRequest,
    RetellBookAppointmentRequest,
)
from backend.app.schemas.api_req_res.call import (
    ActiveCallStatus,
    CallResponse,
    MakeCallRequest,
    StartCallRequest,
    TranscriptsResponse,
)
from backend.app.schemas.api_req_res.common import ErrorResponse
from backend.app.schemas.api_req_res.health import HealthResponse, ReadinessResponse
from backend.app.schemas.api_req_res.patient import PatientOut, ResetPatientsResponse
from backend.app.schemas.api_req_res.provider import FreeSlot, ProviderAvailability, ProvidersAvailabilityResponse
from backend.app.schemas.api_req_res.webhook import RetellWebhookPayload, WebhookAck

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
    "CreateAppointmentRequest",
    "RetellBookAppointmentRequest",
    "AppointmentResponse",
    "AppointmentBookingResponse",
    "RetellWebhookPayload",
    "WebhookAck",
]
