"""POST /api/webhooks/retell — Retell call-lifecycle/transcript events."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services import webhook_service
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/retell")
async def retell_webhook(request: Request):
    # Kept as a manual try/except (rather than the global handler) so a
    # malformed payload from Retell always gets an explicit, logged 500
    # response instead of taking down the connection.
    try:
        payload = await request.json()
        return webhook_service.handle_webhook(payload)
    except Exception as exc:  # noqa: BLE001 - intentional broad catch at the integration boundary
        logger.exception("Error processing Retell webhook")
        return JSONResponse(status_code=500, content={"status": "error", "message": str(exc)})
