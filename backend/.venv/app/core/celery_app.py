# app/core/celery_app.py

from celery import Celery
from .config import settings

celery_app = Celery(
    "lit_summarizer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Optionally, configure Celery from settings:
celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
)

# Autodiscover tasks if they live under app/tasks
celery_app.autodiscover_tasks(["app.tasks"])
