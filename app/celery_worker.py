from celery import Celery
import os
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()

celery_app = Celery(
    "mongo_to_chroma",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.tasks.migrate_task"]
)


celery_app.conf.timezone = "Asia/Seoul"
celery_app.conf.beat_schedule = {}  # Celery Beat가 설정을 여기에 넣음

