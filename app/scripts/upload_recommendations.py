# app/scripts/upload_recommendations.py

import json
from app.clients import db_clients
import asyncio


db = db_clients["recommendation"]

async def upload_recommendation_contents():
    with open("app/data/recommendation_contents.json", "r", encoding="utf-8") as f:
        contents = json.load(f)
    await db.recommendation_content.delete_many({})
    await db.recommendation_content.insert_many(contents)
    print("추천 콘텐츠 업로드 완료!")

if __name__ == "__main__":
    asyncio.run(upload_recommendation_contents())