# mongo_feedback.py
from datetime import datetime
from app.mongodb import db

async def save_feedback_cache(user_id: str, feedback_text: str):
    doc = {
  "user_id": "user123",
  "pre_text": "좋은 코드는 읽기 쉬운 코드입니다.",
  "post_text": "좋은 코드는 재사용성과 유지보수가 좋고 팀에서 협업하기 좋습니다."
}

    await db.feedback_cache.insert_one(doc)

