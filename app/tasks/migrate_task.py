# app/tasks/migrate_task.py
from celery import shared_task
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain_core.documents import Document
from app.clients.chromadb_client import ChromaClient
import os

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_DB_URL"))
collection = mongo["ai_interview"]["interview_contents"]
chroma_client = ChromaClient()

@shared_task
def batch_migrate_to_chroma():
    """MongoDB → ChromaDB 전체 마이그레이션"""
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
                "user_id":  user_id,
                "source_id": str(doc["_id"]),
                "source":   doc.get("source", "interview"),
            }

            # 이미 들어간 문서는 건너뜀
            if chroma_client.collection.get(where={"source_id": metadata["source_id"]}).get("ids"):
                continue

            langchain_docs.append(Document(page_content=content, metadata=metadata))

        if langchain_docs:
            chroma_client.add_documents(langchain_docs)
            print(f"user_id={user_id}: {len(langchain_docs)}개 삽입")
            total += len(langchain_docs)

    print(f"Celery Batch 삽입 완료: 총 {total}개 문서")
