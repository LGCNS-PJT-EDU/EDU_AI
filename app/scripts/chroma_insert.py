from dotenv import load_dotenv
from langchain_core.documents import Document
from pymongo import MongoClient
import os

from app.clients import chroma_client

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_DB_URL"))
db = mongo_client["ai_platform"]
collection = db["recommend_contents"]

contents = list(collection.find({}))

documents = []
for item in contents:
    title = item.get("content_title", "")
    if not title:
        continue

    page_content = f"""
제목: {title}
플랫폼: {item.get("content_platform", "")}
형태: {item.get("content_type", "")}
가격: {item.get("content_price", "")}
소요 시간: {item.get("content_duration", "")}
설명: HTML, CSS, 자바스크립트 관련 자율 학습 콘텐츠입니다.
"""

    doc = Document(
        page_content=page_content.strip(),
        metadata={
            "title": title,
            "url": item.get("content_url", ""),
            "platform": item.get("content_platform", "")
        }
    )
    documents.append(doc)

print(f" 변환된 콘텐츠 수: {len(documents)}")

# 기존 데이터 초기화 (선택)
# shutil.rmtree("chroma_store/recommend_contents")

chroma_client.add_documents(documents)
print(" ChromaDB에 문서 삽입 완료")
