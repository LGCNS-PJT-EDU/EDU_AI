from pymongo import MongoClient
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os

load_dotenv()

# ✅ 정확한 MongoDB 인스턴스 주소 사용
mongo_client = MongoClient("mongodb://54.180.4.224:27017")  # ← 고정 IP로 연결
db = mongo_client["ai_platform"]
collection = db["recommend_contents"]

# ✅ MongoDB 콘텐츠 수 확인
mongo_count = collection.count_documents({})
print(f"✅ MongoDB 콘텐츠 개수: {mongo_count}")

# ✅ ChromaDB 문서 수 확인
embedding = OpenAIEmbeddings()
vectordb = Chroma(
    persist_directory="chroma_store/recommend_contents",
    embedding_function=embedding
)
chroma_count = vectordb._collection.count()
print(f"✅ ChromaDB 벡터 문서 수: {chroma_count}")



