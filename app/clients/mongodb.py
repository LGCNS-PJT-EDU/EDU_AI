from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

#MONGO_URL = "mongodb://localhost:27017"
MONGO_URL = "mongodb://54.180.4.224:27017"
client = AsyncIOMotorClient(MONGO_URL)
db = client["ai_platform"]

async def save_explanation_log(log_data: dict):
    log_data["created_at"] = datetime.utcnow()
    await db.explanation_log.insert_one(log_data)
