from pymongo import MongoClient
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

# ✅ MongoDB 클라이언트 직접 연결
mongo_client = MongoClient("mongodb://54.180.4.224:27017")
db = mongo_client["ai_platform"]

# ✅ Mongo 콘텐츠 출력
mongo_docs = list(db["recommend_contents"].find({}, {
    "_id": 0,
    "total_content_id": 1,
    "content_title": 1,
    "content_type": 1,
    "sub_id": 1
}))
print("✅ MongoDB 콘텐츠 (앞 5개):")
print(pd.DataFrame(mongo_docs[:5]))

# ✅ Chroma 검색
embedding = OpenAIEmbeddings()
vectordb = Chroma(
    persist_directory="chroma_store/recommend_contents",
    embedding_function=embedding
)

chroma_results = vectordb.similarity_search("HTML", k=3)
print("\n✅ Chroma 유사 콘텐츠 검색 결과:")
for doc in chroma_results:
    print(f"- {doc.metadata.get('title')}: {doc.page_content[:50]}")