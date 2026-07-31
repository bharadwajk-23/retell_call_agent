"""Thin wrapper around the Retell Python SDK.

Isolates the third-party SDK behind an interface the rest of the app can
depend on.
"""

from typing import Any, Dict, Optional

from retell import Retell

from backend.app.core import get_logger, get_settings

logger = get_logger(__name__)


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
        if not self._client:
            logger.error("RETELL_API_KEY is not configured; cannot place a real call")
            return None

        dynamic_vars = self._dynamic_variables(
            patient_name, provider_name, exercise_missed_days, phone_number
        )

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

    def get_call_details(self, call_id: str) -> Optional[Any]:
        if not self._client:
            return None
        try:
            return self._client.call.retrieve(call_id)
        except Exception:
            logger.exception("Error retrieving call details for %s", call_id)
            return None


retell_client = RetellClient()
