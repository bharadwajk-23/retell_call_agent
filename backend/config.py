"""
Application configuration via environment variables.
All file paths default under backend/ unless overridden.
"""

import os

from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Load backend/.env when present
load_dotenv(os.path.join(BASE_DIR, ".env"))


def _path(env_key: str, default_relative: str) -> str:
    default = os.path.join(BASE_DIR, default_relative)
    return os.getenv(env_key, default)


def _bool_env(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(default)).lower() in ("1", "true", "yes", "on")


PATIENT_DETAILS_PATH = _path("PATIENT_DETAILS_PATH", "patient_details.json")
PROVIDER_DETAILS_PATH = _path("PROVIDER_DETAILS_PATH", "provider_details.json")
APPOINTMENTS_PATH = _path("APPOINTMENTS_PATH", "appointments.json")
CALL_LOGS_PATH = _path("CALL_LOGS_PATH", "call_logs.json")
FRONTEND_DIR = os.getenv("FRONTEND_DIR", os.path.join(PROJECT_ROOT, "frontend"))

RETELL_API_KEY = os.getenv("RETELL_API_KEY", "")
RETELL_AGENT_ID = os.getenv("RETELL_AGENT_ID", "")
RETELL_FROM_NUMBER = os.getenv("RETELL_FROM_NUMBER", "").strip()
RETELL_MOCK_CALLS = _bool_env("RETELL_MOCK_CALLS", False)

# Slot grid: one entry per hour from 09:00 through 18:00 (10 slots)
SLOT_HOUR_LABELS = [
    "09:00",
    "10:00",
    "11:00",
    "12:00",
    "13:00",
    "14:00",
    "15:00",
    "16:00",
    "17:00",
    "18:00",
]
