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

        # 수정된 부분: .get → [] 방식으로 변경
        self.user_profile = self.db["user_profile"]
        self.recommendation_content = self.db["recommendation_content"]
        self.recommendation_cache = self.db["recommendation_cache"]
        self.feedback = self.db["feedback"]
        self.pre_result = self.db["pre_result"]
        self.post_result = self.db["post_result"]
        self.questions = self.db["questions"]
        self.techMap = self.db["techMap"]
        self.startup_log = self.db["startup_log"]
        self.interview_feedback = self.db["interview_feedback"]
        self.interview_contents = self.db["interview_contents"]

    def get_category_collection(self, category: str):
        return self.db[category]

    async def save_explanation_log(self, log_data: dict):
        log_data["created_at"] = datetime.utcnow()
        await self.db["explanation_log"].insert_one(log_data)


class MongoClientsManager:
    def __init__(self):
        self._clients = {
            "ai_platform": MongoDBClient(db_name="ai_platform"),
            "assessment": MongoDBClient(db_name="assessment"),
            "feedback": MongoDBClient(db_name="feedback"),
            "recommendation": MongoDBClient(db_name="recommendation"),
            "user": MongoDBClient(db_name="ai_platform"),  # user_profile 포함
            "ai_interview": MongoDBClient(db_name="ai_interview"),
        }

    def __getitem__(self, key):
        return self._clients[key]

    @property
    def user_profile(self):
        return self._clients["user"].user_profile

    @property
    def recommendation_content(self):
        return self._clients["recommendation"].recommendation_content

    @property
    def recommendation_cache(self):
        return self._clients["recommendation"].recommendation_cache

    @property
    def feedback(self):
        return self._clients["feedback"].feedback

    @property
    def pre_result(self):
        return self._clients["assessment"].pre_result

    @property
    def post_result(self):
        return self._clients["assessment"].post_result

    @property
    def questions(self):
        return self._clients["ai_platform"].questions

    @property
    def techMap(self):
        return self._clients["ai_platform"].techMap

    @property
    def startup_log(self):
        return self._clients["ai_platform"].startup_log

    @property
    def interview_feedback(self):
        return self._clients["ai_interview"].interview_feedback

    @property
    def interview_contents(self):
        return self._clients["ai_interview"].interview_contents
