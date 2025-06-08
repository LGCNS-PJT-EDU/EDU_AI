from celery import shared_task
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from langchain_core.documents import Document
from app.clients.chromadb_client import ChromaClient

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_DB_URL"))
collection = mongo["ai_interview"]["interview_contents"]
chroma_client = ChromaClient()

@shared_task
def batch_sync_all_sources():
    from app.services.sync.sync_recommend import sync_recommendation
    from app.services.sync.sync_feedback import sync_feedback
    from app.services.sync.sync_assessments import sync_pre, sync_post

    print(" 모든 소스 동기화 시작")
    sync_recommendation()
    sync_feedback()
    sync_pre()
    sync_post()

@shared_task
def batch_migrate_to_chroma():
    user_ids = collection.distinct("user_id")
    total = 0

    for user_id in user_ids:
        docs = collection.find({"user_id": user_id})
        langchain_docs = []

        for doc in docs:
            content = doc.get("content", "")
            if not content:
                continue
            metadata = {"user_id": user_id, "source_id": str(doc["_id"])}
            langchain_docs.append(Document(page_content=content, metadata=metadata))

        if langchain_docs:
            chroma_client.add_documents(langchain_docs)
            print(f" user_id={user_id}: {len(langchain_docs)}개 삽입")
            total += len(langchain_docs)

    print(f" Celery Batch 전체 삽입 완료: 총 {total}개 문서")