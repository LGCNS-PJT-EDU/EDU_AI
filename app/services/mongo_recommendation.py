# app/services/mongo_recommendation.py

from app.clients.mongodb import db
from datetime import datetime

async def get_recommended_contents_by_subject(subject_name: str):
    results = await db.recommendation_contents.find({"subject_name": subject_name}).to_list(length=None)
    return results
