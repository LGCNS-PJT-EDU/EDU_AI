from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os

from pymongo import MongoClient

from app.clients import chroma_client

load_dotenv()

# ✅ MongoDB 연결
mongo_client = MongoClient(os.getenv("MONGO_DB_URL"))
db = mongo_client["ai_platform"]
collection = db["recommend_contents"]

# ✅ MongoDB에서 콘텐츠 불러오기
contents = list(collection.find({}))

# ✅ Chroma에 넣을 문서 생성
documents = []
for item in contents:
    title = item.get("content_title")
    if not title:
        continue

    page_content = f"{title} 관련 콘텐츠입니다. HTML, 웹 개발, 기초 태그 등을 다룹니다."
    doc = Document(
        page_content=page_content,
        metadata={"title": title}
    )
    documents.append(doc)

print(f"✅ 변환된 콘텐츠 수: {len(documents)}")

# ✅ 임베딩 객체 생성
emb = chroma_client

# ✅ 원격 서버에 문서 업로드
vectordb = Chroma.from_documents(
    documents=documents,
    embedding=emb.embedding,
    persist_directory="chroma_store/recommend_contents",  # HTTP 모드에선 무시
    client_settings=emb.settings,
    client=emb.client._client,
    collection_name="recommend_contents"
)

print("✅ ChromaDB에 저장 완료")