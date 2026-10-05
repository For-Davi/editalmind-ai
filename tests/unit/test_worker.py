import subprocess
import sys

from celery import Celery

from editalmind_ai.infrastructure.settings import Settings
from editalmind_ai.presentation.tasks.system import ping
from editalmind_ai.worker import TASK_MODULES, create_celery


def make_eager_app() -> Celery:
    return create_celery(
        Settings(_env_file=None, environment="test", celery_task_always_eager=True)
    )


def test_ping_returns_pong() -> None:
    assert ping() == "pong"


def test_ping_runs_through_celery_in_eager_mode() -> None:
    app = make_eager_app()

    result = app.tasks["system.ping"].delay()

    assert result.successful()
    assert result.get() == "pong"


def test_celery_uses_json_and_late_acknowledgement() -> None:
    app = make_eager_app()

    assert app.conf.task_serializer == "json"
    assert app.conf.accept_content == ["json"]
    assert app.conf.task_acks_late is True
    assert app.conf.worker_prefetch_multiplier == 1


def test_tasks_are_registered_for_producers_in_a_fresh_process() -> None:
    script = "from editalmind_ai.worker import app; print('system.ping' in app.tasks)"

    completed = subprocess.run(  # noqa: S603
        [sys.executable, "-c", script], capture_output=True, text=True, check=True
    )

    assert completed.stdout.strip() == "True"
    assert TASK_MODULES == ["editalmind_ai.presentation.tasks.system"]


def test_broker_and_backend_come_from_settings() -> None:
    app = create_celery(Settings(_env_file=None, redis_url="redis://cache:6380/2"))

    assert app.conf.broker_url == "redis://cache:6380/2"
    assert app.conf.result_backend == "redis://cache:6380/2"
