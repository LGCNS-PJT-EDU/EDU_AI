import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDBClient:
    def __init__(self, mongo_url: str | None = None, db_name: str = "ai_platform"):
        url = os.getenv("MONGO_DB_URL")
        if not url:
            raise RuntimeError("MongoDB URL not found")

        self.client = AsyncIOMotorClient(url)
        self.db = self.client[db_name]

        # db_name = user
        self.user_profile = self.db["user_profile"]

        # db_name = recommendation
        self.recommendation_content = self.db["recommendation_content"]
        self.recommendation_cache = self.db["recommendation_cache"]

        # db_name = feedback
        self.feedback = self.db["feedback"]

        # db_name = assessment
        self.pre_result = self.db["pre_result"]
        self.post_result = self.db["post_result"]

        # db_name = ai_platform
        self.techMap = self.db["techMap"]


    async def save_explanation_log(self, log_data: dict):
        log_data["created_at"] = datetime.utcnow()
        await self.explanation_log.insert_one(log_data)