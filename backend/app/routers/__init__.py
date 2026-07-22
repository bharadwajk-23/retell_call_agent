"""API routers, one module per resource: health, patients, calls, providers, appointments, webhooks.

Combined into a single `router` here so app/main.py only has to mount one.
Each submodule's own `APIRouter` is still named `router` internally, hence
the module-qualified access below rather than a flat re-export (they'd
collide under one name otherwise).
"""

from fastapi import APIRouter

from backend.app.routers import appointments, calls, health, patients, providers, webhooks

router = APIRouter()
router.include_router(health.router)
router.include_router(patients.router)
router.include_router(calls.router)
router.include_router(providers.router)
router.include_router(appointments.router)
router.include_router(webhooks.router)

__all__ = ["router"]
