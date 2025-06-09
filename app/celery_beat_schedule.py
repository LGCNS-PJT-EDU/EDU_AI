from app.celery_worker import celery_app
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "daily-migrate-all": {
        "task": "app.tasks.migrate_task.batch_sync_all_sources",
        "schedule": crontab(hour=3, minute=0),  # 매일 새벽 3시
    },
}
