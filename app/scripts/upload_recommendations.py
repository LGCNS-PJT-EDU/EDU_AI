# app/scripts/upload_recommendations.py

import json
from app.clients.mongodb import db
import asyncio

async def upload_recommendation_contents():
    with open("app/data/recommendation_contents.json", "r", encoding="utf-8") as f:
        contents = json.load(f)
    await db.recommendation_contents.delete_many({})
    await db.recommendation_contents.insert_many(contents)
    print("추천 콘텐츠 업로드 완료!")

if __name__ == "__main__":
    asyncio.run(upload_recommendation_contents())