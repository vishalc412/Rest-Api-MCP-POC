from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "vitaclan",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_routes={
        "app.worker.tasks.process_ocr_task": {"queue": "ocr"},
        "app.worker.tasks.send_medication_reminders": {"queue": "reminders"},
    },
    beat_schedule={
        # Fire reminder checks every minute
        "medication-reminders": {
            "task": "app.worker.tasks.send_medication_reminders",
            "schedule": 60.0,
        },
    },
)
