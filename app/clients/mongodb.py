import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient


class MongoDBClient:
    def __init__(self, mongo_url: str | None = None, db_name: str = "ai_platform"):
        url = mongo_url or os.getenv("MONGO_DB_URL")
        if not url:
            raise RuntimeError("MongoDB URL not found")

        self.client = AsyncIOMotorClient(url)
        self.db = self.client[db_name]  # 주입 가능성을 위해 유지 (기본: ai_platform)

        # ===== ai_platform DB =====
        ai_platform_db = self.client["ai_platform"]
        self.user_profile = ai_platform_db["user_profile"]
        self.recommendation_content = ai_platform_db["recommendation_content"]
        self.recommendation_cache = ai_platform_db["recommend_cache"]  # ✅ 실제 컬렉션명 일치
        self.techMap = ai_platform_db["techMap"]
        self.questions = ai_platform_db["questions"]

        # ===== feedback DB =====
        feedback_db = self.client["feedback"]
        self.feedback = feedback_db["feedback_content"]  # ✅ 수정됨

        # ===== assessment DB =====
        assessment_db = self.client["assessment"]
        self.pre_result = assessment_db["pre_result"]
        self.post_result = assessment_db["post_result"]

        # ===== ai_interview DB =====
        ai_interview_db = self.client["ai_interview"]
        self.interview_feedback = ai_interview_db["interview_contents"]  # ✅ 인터뷰 저장소

        # ===== local DB =====
        local_db = self.client["local"]
        self.startup_log = local_db["startup_log"]  # ✅ 시스템 이벤트 로그

    def get_category_collection(self, category: str):
        return self.db[category]

    async def save_explanation_log(self, log_data: dict):
        log_data["created_at"] = datetime.utcnow()
        await self.startup_log.insert_one(log_data)  # ✅ 수정됨: 시스템 로그로 저장
