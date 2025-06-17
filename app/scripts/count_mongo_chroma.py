from pymongo import MongoClient
from dotenv import load_dotenv

from app.clients import chroma_client

load_dotenv()

#  정확한 MongoDB 인스턴스 주소 사용
mongo_client = MongoClient("mongodb://54.180.4.224:27017")  # ← 고정 IP로 연결
db = mongo_client["recommendation"]
collection = db.recommendation_content

#  MongoDB 콘텐츠 수 확인
mongo_count = collection.count_documents({})
print(f" MongoDB 콘텐츠 개수: {mongo_count}")

#  ChromaClient 객체 생성
client = chroma_client.client._client

#  HTTP-only 모드로 원격 ChromaDB의 정보를 가져옴
coll = client.get_collection(name="recommend_contents")
chroma_count = coll.count()

print(f" ChromaDB 벡터 문서 수: {chroma_count}")