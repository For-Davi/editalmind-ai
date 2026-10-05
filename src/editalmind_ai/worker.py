"""Composition root of the Celery workers: `celery -A editalmind_ai.worker worker`."""

from importlib import import_module

from celery import Celery

from editalmind_ai.infrastructure.settings import Settings, get_settings

TASK_MODULES = ["editalmind_ai.presentation.tasks.system"]


def create_celery(settings: Settings) -> Celery:
    app = Celery("editalmind_ai", broker=settings.redis_url, backend=settings.redis_url)
    app.conf.update(
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        task_acks_late=True,
        task_reject_on_worker_lost=True,
        worker_prefetch_multiplier=1,
        task_always_eager=settings.celery_task_always_eager,
        broker_connection_retry_on_startup=True,
    )
    # `include` is only honoured by workers; importing here registers tasks for producers too.
    for module in TASK_MODULES:
        import_module(module)
    return app


app = create_celery(get_settings())
