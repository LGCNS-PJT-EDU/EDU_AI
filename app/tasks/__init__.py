# app/tasks/__init__.py
from celery import Celery
from celery.schedules import crontab
import os
from dotenv import load_dotenv

load_dotenv()

celery_app = Celery(
    "mongo_to_chroma",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.tasks.migrate_task"]
)

celery_app.conf.timezone = "Asia/Seoul"
celery_app.conf.beat_schedule = {
    "daily-migrate-to-chroma": {
        "task": "app.tasks.migrate_task.batch_migrate_to_chroma",
        "schedule": crontab(hour=3, minute=0),
    }
}
# 제일 마지막 줄에 추가:pip install -U redis==4.6.0
celery = celery_app