from pymongo import MongoClient
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from dotenv import load_dotenv
import os

load_dotenv()

# ✅ MongoDB 연결
mongo_client = MongoClient(os.getenv("MONGO_URI"))
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

# ✅ Chroma 저장
embedding = OpenAIEmbeddings()
vectordb = Chroma.from_documents(
    documents=documents,
    embedding=embedding,
    persist_directory="chroma_store/recommend_contents"
)

print("✅ ChromaDB에 저장 완료")  # ← 여기가 종료점입니다




