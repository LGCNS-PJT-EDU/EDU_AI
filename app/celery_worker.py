# celery_worker.py
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "ai_tasks",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "app.tasks.migrate_task",
        "app.tasks.feedback_task"
    ]
)

celery_app.conf.timezone = "Asia/Seoul"
celery_app.conf.beat_schedule = {
    "daily-migrate-to-chroma": {
        "task": "app.tasks.migrate_task.batch_migrate_to_chroma",
        "schedule": crontab(hour=3, minute=0),
    },
    "daily-sync-feedback-to-opensearch": {
        "task": "app.tasks.migrate_task.sync_feedback_logs_to_opensearch",
        "schedule": crontab(hour=4, minute=0),
    },
}
