from pymongo import MongoClient, ASCENDING
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB 연결
client = MongoClient(os.getenv("MONGO_DB_URL"))
db = client["ai_platform"]

# recommend_reason_cache 인덱스 생성
index_name = db["recommend_reason_cache"].create_index(
    [("title", ASCENDING), ("user_context", ASCENDING)],
    unique=True
)

print(f" 인덱스 생성 완료: {index_name}")
