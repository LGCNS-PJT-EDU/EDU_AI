# ✅ 통합 테스트용 스크립트: test_rag_pipeline.py
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from langchain_core.documents import Document
from app.clients.chromadb_client import ChromaClient
from app.services.rag_module import retrieve_similar_docs, retrieve_personalized_docs

load_dotenv()

# Mongo 연결
mongo = MongoClient(os.getenv("MONGO_DB_URL"))
collection = mongo["ai_interview"]["interview_contents"]

# Chroma Client
chroma_client = ChromaClient()

def test_batch_embedding():
    print("\n[1] Mongo → Chroma 임베딩 테스트")
    user_ids = collection.distinct("user_id")
    total = 0
    for user_id in user_ids:
        docs = collection.find({"user_id": user_id})
        langchain_docs = []
        for doc in docs:
            content = doc.get("content", "")
            if not content:
                continue
            metadata = {
                "user_id": user_id,
                "source_id": str(doc["_id"]),
                "source": doc.get("source", "interview")
            }
            langchain_docs.append(Document(page_content=content, metadata=metadata))

        if langchain_docs:
            chroma_client.add_documents(langchain_docs)
            print(f" - user_id={user_id}: {len(langchain_docs)}개 삽입")
            total += len(langchain_docs)
    print(f"\n 전체 삽입 완료: 총 {total}개 문서")

def test_rag_retrieval():
    print("\n[2] RAG 검색 테스트")
    sample_query = "자기소개는 어떻게 말해야 하나요?"
    global_results = retrieve_similar_docs(sample_query)
    personal_results = retrieve_personalized_docs(user_id="2", query=sample_query)

    print("\n [Global] 유사 문서:")
    for i, res in enumerate(global_results, 1):
        print(f"  {i}. {res[:80]}...")

    print("\n [User 2] 개인화 유사 문서:")
    for i, res in enumerate(personal_results, 1):
        print(f"  {i}. {res[:80]}...")

if __name__ == "__main__":
    test_batch_embedding()
    test_rag_retrieval()
