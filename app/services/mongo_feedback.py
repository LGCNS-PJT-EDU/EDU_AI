# mongo_feedback.py
from datetime import datetime
from app.clients.mongodb import db

async def save_feedback_cache(user_id: str, feedback_text: str):
    doc = {
        "user_id": user_id,
        "feedback": feedback_text,
        "created_at": datetime.utcnow()
    }
    await db.feedback_cache.insert_one(doc)


