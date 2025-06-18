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
        "app.tasks.feedback_task",
        "app.tasks.opensearch_task",
    ],
)

# 모듈을 미리 import 해 두면 워커 기동 시 태스크가 즉시 등록됩니다.
import app.tasks.migrate_task
import app.tasks.feedback_task
import app.tasks.opensearch_task

celery_app.conf.beat_schedule = {
    # 매일 03:00 MongoDB → Chroma 마이그레이션
    "daily-migrate-to-chroma": {
        "task": "app.tasks.migrate_task.batch_migrate_to_chroma",
        "schedule": crontab(hour=3, minute=0),
    },
    # 매일 04:00 Feedback → OpenSearch 전송  (경로 수정!)
    "daily-sync-feedback-to-opensearch": {
        "task": "app.tasks.feedback_task.sync_feedback_logs_to_opensearch",
        "schedule": crontab(hour=4, minute=0),
    },
    # 매일 05:00 모든 로그 컬렉션 → OpenSearch
    "daily-sync-opensearch-logs": {
        "task": "sync_all_logs_to_opensearch",
        "schedule": crontab(hour=5, minute=0),
    },
}
