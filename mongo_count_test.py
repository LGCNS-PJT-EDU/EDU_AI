from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일에서 환경변수 불러오기

mongo = MongoClient(os.getenv("MONGO_DB_URL"))
collection = mongo["ai_interview"]["interview_contents"]

count = collection.count_documents({})
print(f"interview_contents 컬렉션 내 문서 개수: {count}")
