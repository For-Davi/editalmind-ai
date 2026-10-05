from importlib.metadata import version

import pytest
from httpx import ASGITransport, AsyncClient

from editalmind_ai.infrastructure.settings import Settings
from editalmind_ai.main import create_app

pytestmark = pytest.mark.integration


async def test_health_reports_service_status() -> None:
    app = create_app(Settings(_env_file=None, environment="test"))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "editalmind-ai",
        "version": version("editalmind-ai"),
        "environment": "test",
    }


async def test_docs_are_hidden_in_production() -> None:
    app = create_app(Settings(_env_file=None, environment="production"))

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/docs")

    assert response.status_code == 404
