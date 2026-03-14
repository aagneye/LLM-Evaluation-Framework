"""
Worker configuration for async task execution.

This module sets up Celery for background task processing.
For simpler deployments, FastAPI BackgroundTasks can be used instead.
"""

from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "llm_eval_worker",
    broker=settings.redis_url,
    backend=settings.redis_url
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Import tasks
from app.workers import tasks
