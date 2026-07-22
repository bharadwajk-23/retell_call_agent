"""POST /webhooks/retell — Retell call-lifecycle/transcript events."""

from fastapi import APIRouter, Request

from backend.app.schemas.webhook import RetellWebhookPayload, WebhookAck
from backend.app.services import webhook_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/retell", response_model=WebhookAck)
async def retell_webhook(request: Request, payload: RetellWebhookPayload) -> WebhookAck:
    """Malformed JSON bodies are already handled by the global validation
    handler; any other failure propagates to the global exception handler."""
    body = await request.body()
    signature = request.headers.get("x-retell-signature", "")
    webhook_service.verify_signature(body, signature)

    result = webhook_service.handle_webhook(payload.model_dump(exclude_none=True))
    return WebhookAck(**result)
