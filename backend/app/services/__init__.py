"""Business logic, one module per resource: patient, call, health, provider, appointment, webhook.

Routers import these modules directly (e.g. `from backend.app.services import
call_service`) rather than individual functions, to keep call sites
unambiguous about which resource a function belongs to.
"""
