"""Centralized literals that were previously hardcoded inline across the app."""

# --- API metadata (app/main.py) ---
API_TITLE = "AI Physiotherapy Call Agent API"
API_VERSION = "2.0.0"

# --- Call lifecycle (app/services/call_service.py) ---
# Status of our own ActiveCall record that means the call is over.
TERMINAL_CALL_STATUSES = {"completed", "ended", "not_connected", "error"}
# Status reported by Retell's call-details API. Deliberately excludes
# "completed" here (unlike TERMINAL_CALL_STATUSES above) — a "completed"
# details_status falls through to the staleness check in the original logic.
DETAILS_TERMINAL_STATUSES = {"ended", "not_connected", "error"}
ACTIVE_CALL_STATUSES = {"registered", "ongoing"}

# --- Retell custom-function defaults (app/schemas/appointment.py) ---
# Defaults intentionally mirror the original implementation so the voice
# agent's existing custom-function configuration keeps working unchanged.
DEFAULT_PROVIDER_NAME = "Bharadwaj"
DEFAULT_SLOT_WEEKDAY = "Monday"
DEFAULT_SLOT_TIME = "09:00 am"
