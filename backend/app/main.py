"""
FastAPI application entrypoint for the AI Physiotherapy Call Agent backend.

This service is API-only: it never serves the React frontend. Run the
frontend as its own process (see ../frontend) and point it at this API via
VITE_API_BASE_URL.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import get_settings
from backend.app.core.constants import API_TITLE, API_VERSION
from backend.app.core.logging import configure_logging, get_logger
from backend.app.middleware.error_handlers import register_exception_handlers
from backend.app.middleware.request_logging import RequestLoggingMiddleware
from backend.app.routers import appointments, calls, health, patients, providers, webhooks

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Starting AI Physiotherapy Call Agent API")
    if not settings.RETELL_API_KEY:
        logger.warning("RETELL_API_KEY is not set — outbound calls will fail")
    yield
    logger.info("Shutting down AI Physiotherapy Call Agent API")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=API_TITLE,
        version=API_VERSION,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(patients.router)
    app.include_router(calls.router)
    app.include_router(providers.router)
    app.include_router(appointments.router)
    app.include_router(webhooks.router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
