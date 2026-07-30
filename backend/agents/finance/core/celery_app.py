from celery import Celery
from core.config import settings

celery_app = Celery(
    "abcc_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Optional: define a test task
@celery_app.task
def test_celery_task(word: str) -> str:
    return f"Celery is working: {word}"
