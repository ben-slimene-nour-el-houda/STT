from celery import Celery
from common.settings import settings

celery_app = Celery(
    "stt_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Optional: configure task serialization and time limits
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=3600,  # seconds (increase to 1 hour)
    task_soft_time_limit=3400,  # optional soft limit
)
import worker.tasks  # Ensure task registration
