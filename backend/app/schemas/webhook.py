"""Request/response schemas for the Retell webhook endpoint."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class RetellWebhookPayload(BaseModel):
    """Retell call-lifecycle/transcript webhook body.

    Extra fields are allowed (and preserved) because Retell's payload shape
    varies by event type; only the fields this service actually reads are
    declared explicitly.
    """

    model_config = ConfigDict(extra="allow")

    event: Optional[str] = None
    call_id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class WebhookAck(BaseModel):
    status: str
