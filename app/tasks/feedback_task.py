# app/tasks/feedback_task.py
from celery import shared_task
from app.utils.embed import embed_to_chroma

@shared_task(name="sync_feedback_to_chroma")
def sync_feedback_to_chroma_task(user_id: str, content: str, source_id: str):
    return embed_to_chroma(
        user_id=user_id,
        content=content,
        source="feedback",
        source_id=source_id
    )
