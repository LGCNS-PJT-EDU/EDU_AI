# app/tasks/migrate_task.py
from celery import shared_task
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
from app.clients.chromadb_client import ChromaClient
from langchain_core.documents import Document
from opensearchpy.helpers import bulk
from app.clients.opensearch_client import opensearch_client
import os

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_DB_URL"))
collection = mongo["ai_interview"]["interview_contents"]
chroma_client = ChromaClient()

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

            metadata = {
                "user_id": user_id,
                "source_id": str(doc["_id"]),
                "source": doc.get("source", "interview")
            }

            existing = chroma_client.collection.get(where={"source_id": metadata["source_id"]})
            if existing.get("ids"):
                continue

            langchain_docs.append(Document(page_content=content, metadata=metadata))

        if langchain_docs:
            chroma_client.add_documents(langchain_docs)
            print(f" user_id={user_id}: {len(langchain_docs)}개 삽입")
            total += len(langchain_docs)

    print(f" Celery Batch 삽입 완료: 총 {total}개 문서")

@shared_task
def sync_feedback_logs_to_opensearch():
    import asyncio
    actions = []
    cursor = collection.find({})
    for doc in cursor:
        actions.append({
            "_index": "feedback_logs",
            "_id": str(doc["_id"]),
            "_source": {
                "user_id": doc.get("user_id"),
                "feedback_type": doc.get("feedback_type", "post"),
                "subject": doc.get("subject"),
                "final_comment": doc.get("final_comment"),
                "score": doc.get("score", 0),
                "timestamp": doc.get("timestamp", datetime.utcnow()),
                "embedding": doc.get("embedding", [0.0] * 768)
            }
        })
    if actions:
        success, _ = bulk(opensearch_client, actions)
        print(f"OpenSearch 전송 완료: {success}개 문서")
    else:
        print("MongoDB에서 읽은 문서가 없습니다!")
