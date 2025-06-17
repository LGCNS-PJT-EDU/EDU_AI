from celery import shared_task
from pymongo import MongoClient
from dotenv import load_dotenv

import os
from langchain_core.documents import Document
from app.clients.chromadb_client import ChromaClient
from app.clients.opensearch_client import opensearch_client

load_dotenv()
mongo = MongoClient(os.getenv("MONGO_DB_URL"))
collection = mongo["ai_interview"]["interview_contents"]
feedback_collection = mongo["ai_platform"]["feedback"]
chroma_client = ChromaClient()

@shared_task
def sync_feedback_logs_to_opensearch():  # ⬅ 추가
    """
    MongoDB 'feedback' 컬렉션을 OpenSearch로 전송하는 작업.
    """
    from opensearchpy.helpers import bulk  # ⬅ 추가

    feedback_docs = list(feedback_collection.find())

    actions = []
    for doc in feedback_docs:
        action = {
            "_index": "feedback_logs",
            "_id": str(doc["_id"]),
            "_source": {
                "user_id": doc.get("user_id"),
                "question_id": doc.get("question_id"),
                "score": doc.get("score"),
                "reason": doc.get("reason"),
                "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None
            }
        }
        actions.append(action)

    success, _ = bulk(opensearch_client, actions)
    print(f"[OpenSearch] {success}개 문서 전송 완료")  # ⬅ 추가


@shared_task
def batch_sync_all_sources():
    try:
        from app.services.sync.sync_recommend import sync_recommendation
        from app.services.sync.sync_feedback import sync_feedback
        from app.services.sync.sync_assessments import sync_pre, sync_post
        from app.services.sync.sync_inrweview import sync_evaluator

        print(" 모든 소스 동기화 시작")
        sync_recommendation()
        sync_feedback()
        sync_pre()
        sync_post()
        sync_evaluator()

    except ModuleNotFoundError:
        print("⚠ sync 모듈 경로 확인 필요: app/services/sync/*")

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

            # 중복 체크: 이미 같은 source_id가 있는 경우 건너뜀
            existing = chroma_client.collection.get(where={"source_id": metadata["source_id"]})
            if existing.get("ids"):
                continue

            langchain_docs.append(Document(page_content=content, metadata=metadata))

        if langchain_docs:
            chroma_client.add_documents(langchain_docs)
            print(f" user_id={user_id}: {len(langchain_docs)}개 삽입")
            total += len(langchain_docs)

    print(f" Celery Batch 삽입 완료: 총 {total}개 문서")
