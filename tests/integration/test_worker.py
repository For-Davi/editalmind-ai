from collections.abc import Iterator

import pytest
from celery import Celery
from celery.contrib.testing.worker import start_worker
from testcontainers.community.redis import RedisContainer

from editalmind_ai.infrastructure.settings import Settings
from editalmind_ai.worker import create_celery

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def redis_url() -> Iterator[str]:
    with RedisContainer("redis:7.4-alpine") as redis:
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)
        yield f"redis://{host}:{port}/0"


@pytest.fixture
def celery_app(redis_url: str) -> Celery:
    return create_celery(Settings(_env_file=None, environment="test", redis_url=redis_url))


def test_worker_consumes_ping_from_redis(celery_app: Celery) -> None:
    with start_worker(celery_app, pool="solo", perform_ping_check=False):
        result = celery_app.tasks["system.ping"].delay()

        assert result.get(timeout=10) == "pong"
        assert result.state == "SUCCESS"
