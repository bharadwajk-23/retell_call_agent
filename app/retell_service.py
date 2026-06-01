"""
Retell AI service — outbound phone calls.
"""

import uuid
from typing import Any, Dict, Optional

from retell import Retell

import app.config as config

client = Retell(api_key=config.RETELL_API_KEY)


class MockCallResponse:
    """Minimal stand-in when RETELL_MOCK_CALLS=true."""

    def __init__(self, call_id: str):
        self.call_id = call_id


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
    phone_number: str,
    from_number: str,
    patient_name: str,
    provider_name: str,
    exercise_missed_days: int,
    agent_id: Optional[str] = None,
) -> Optional[Any]:
    """
    Start an outbound call via Retell (Telnyx/Twilio number must be in Retell as from_number).
    """
    dynamic_vars = _dynamic_variables(
        patient_name, provider_name, exercise_missed_days, phone_number
    )

    if config.RETELL_MOCK_CALLS:
        return MockCallResponse(call_id=f"mock_{uuid.uuid4().hex[:12]}")

    if not config.RETELL_API_KEY:
        print("Error: RETELL_API_KEY is not set.")
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
        return client.call.create_phone_call(**kwargs)
    except Exception as e:
        print(f"Error triggering call: {e}")
        return None


def get_call_details(call_id: str):
    if config.RETELL_MOCK_CALLS:
        return {"call_id": call_id, "status": "mock"}
    try:
        return client.call.retrieve(call_id)
    except Exception as e:
        print(f"Error retrieving call details: {e}")
        return None
