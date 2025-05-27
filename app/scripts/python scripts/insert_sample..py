from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["ai_platform"]
collection = db["recommend_contents"]

sample_data = [
    {
        "total_content_id": 1,
        "content_title": "생활코딩 - HTML",
        "content_url": "https://www.youtube.com/watch?v=tZooW6PritE",
        "content_type": "동영상",
        "content_platform": "유튜브",
        "content_duration": "HOUR_3",
        "content_level": "하",
        "content_price": "FREE",
        "sub_id": 1
    },
    {
        "total_content_id": 2,
        "content_title": "HTML 태그 정리",
        "content_url": "https://www.youtube.com/watch?v=T7h8O7dpJIg",
        "content_type": "동영상",
        "content_platform": "유튜브",
        "content_duration": "HOUR_1",
        "content_level": "하",
        "content_price": "FREE",
        "sub_id": 1
    }
]

collection.insert_many(sample_data)
print("✅ MongoDB에 샘플 콘텐츠 삽입 완료")
