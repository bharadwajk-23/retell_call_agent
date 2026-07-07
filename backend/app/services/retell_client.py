"""Thin wrapper around the Retell Python SDK.

Isolates the third-party SDK behind an interface the rest of the app can
depend on, and centralizes mock-mode handling for local development/demos.
"""

import uuid
from typing import Any, Dict, Optional

from retell import Retell

from app.config.settings import get_settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)


class MockCallResponse:
    """Minimal stand-in used when RETELL_MOCK_CALLS=true."""

    def __init__(self, call_id: str):
        self.call_id = call_id
        self.call_status = "mock"


class RetellClient:
    def __init__(self) -> None:
        settings = get_settings()
        self._settings = settings
        self._client: Optional[Retell] = None
        if settings.RETELL_API_KEY:
            self._client = Retell(api_key=settings.RETELL_API_KEY)

    @staticmethod
    def _dynamic_variables(
        patient_name: str,
        provider_name: str,
        exercise_missed_days: int,
        phone_number: str,
    ) -> Dict[str, str]:
        return {
            "patient_name": patient_name,
            "doctor_name": provider_name,
            "provider_name": provider_name,
            "exercise_missed_days": str(exercise_missed_days),
            "phone": phone_number,
        }

    def trigger_outbound_call(
        self,
        phone_number: str,
        from_number: str,
        patient_name: str,
        provider_name: str,
        exercise_missed_days: int,
        agent_id: Optional[str] = None,
    ) -> Optional[Any]:
        dynamic_vars = self._dynamic_variables(
            patient_name, provider_name, exercise_missed_days, phone_number
        )

        if self._settings.RETELL_MOCK_CALLS:
            logger.info("Mock call placed to %s", phone_number)
            return MockCallResponse(call_id=f"mock_{uuid.uuid4().hex[:12]}")

        if not self._client:
            logger.error("RETELL_API_KEY is not configured; cannot place a real call")
            return None

        try:
            kwargs: Dict[str, Any] = {
                "from_number": from_number,
                "to_number": phone_number,
                "retell_llm_dynamic_variables": dynamic_vars,
                "metadata": dynamic_vars,
            }
            if agent_id:
                kwargs["override_agent_id"] = agent_id
            return self._client.call.create_phone_call(**kwargs)
        except Exception:
            logger.exception("Error triggering outbound call to %s", phone_number)
            return None

    def get_call_details(self, call_id: str):
        if self._settings.RETELL_MOCK_CALLS:
            return {"call_id": call_id, "call_status": "mock"}
        if not self._client:
            return None
        try:
            return self._client.call.retrieve(call_id)
        except Exception:
            logger.exception("Error retrieving call details for %s", call_id)
            return None


retell_client = RetellClient()
