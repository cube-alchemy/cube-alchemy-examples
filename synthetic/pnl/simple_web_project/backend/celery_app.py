from celery import Celery
from .core.config import settings

celery_app = Celery(
    "cube_backend",
    broker=settings.broker_url,
    backend=settings.result_backend,
)

celery_app.conf.update(
    task_serializer="pickle",
    result_serializer="pickle",
    accept_content=["pickle", "json"],
    timezone="UTC",
    enable_utc=True,
)
