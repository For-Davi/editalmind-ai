"""Composition root of the internal HTTP API."""

from importlib.metadata import version

from fastapi import FastAPI

from editalmind_ai.infrastructure.settings import Settings, get_settings
from editalmind_ai.presentation.http import health


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()

    app = FastAPI(
        title="EditalMind AI",
        version=version("editalmind-ai"),
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.state.settings = settings
    app.include_router(health.router)
    return app
