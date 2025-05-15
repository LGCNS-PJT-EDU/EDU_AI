from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client["ai_platform"]

async def save_explanation_log(log_data: dict):
    log_data["created_at"] = datetime.utcnow()
    await db.explanation_log.insert_one(log_data)
