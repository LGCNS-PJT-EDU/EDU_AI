import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(os.getenv("MONGO_DB_URL"))
db = client["ai_platform"]


class MongoDBClient:
    def __init__(self, mongo_url: str | None = None, db_name: str = "ai_platform"):
        url = os.getenv("MONGO_DB_URL")
        if not url:
            raise RuntimeError("MongoDB URL not found")

        self.client = AsyncIOMotorClient(url)
        self.db = self.client[db_name]

        self.recommend_contents = self.db["recommend_contents"]
        self.user_profiles = self.db["user_profiles"]
        self.recommend_cache = self.db["recommend_cache"]


    async def save_explanation_log(self, log_data: dict):
        log_data["created_at"] = datetime.utcnow()
        await self.explanation_log.insert_one(log_data)