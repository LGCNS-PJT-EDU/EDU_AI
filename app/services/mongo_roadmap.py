# app/mongo_roadmap.py

from app.clients.mongodb import db
from datetime import datetime

async def save_roadmap_cache(user_id, roadmap):
    doc = {
        "user_id": user_id,
        "roadmap": roadmap,
        "created_at": datetime.utcnow()
    }
    await db.roadmap_cache.insert_one(doc)


