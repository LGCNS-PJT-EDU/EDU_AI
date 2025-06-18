# app/tasks/feedback_task.py
from celery import shared_task
from datetime import datetime
from pymongo import MongoClient
from opensearchpy.helpers import bulk
from app.clients.opensearch_client import opensearch_client
from app.utils.embed import embed_to_chroma

# ──────────────────────────────────────────────
# 1) Chroma 삽입용 태스크
# ──────────────────────────────────────────────
@shared_task(name="sync_feedback_to_chroma")
def sync_feedback_to_chroma_task(user_id: str, content: str, source_id: str):
    """사용자 피드백을 임베딩 후 ChromaDB에 저장"""
    return embed_to_chroma(
        user_id=user_id,
        content=content,
        source="feedback",
        source_id=source_id,
    )

# ──────────────────────────────────────────────
# 2) OpenSearch 로그 적재 태스크 (동기 PyMongo 버전)
# ──────────────────────────────────────────────
mongo = MongoClient("mongodb://localhost:27017")
collection = mongo["feedback"]["feedback_content"]

@shared_task(name="sync_feedback_logs_to_opensearch")
def sync_feedback_logs_to_opensearch():
    """feedback_content → OpenSearch 인덱스(feedback_logs)"""
    actions = [
        {
            "_index": "feedback_logs",
            "_id": str(doc["_id"]),
            "_source": {
                "user_id":       doc.get("user_id"),
                "feedback_type": doc.get("feedback_type", "post"),
                "subject":       doc.get("subject"),
                "final_comment": doc.get("final_comment"),
                "score":         doc.get("score", 0),
                "timestamp":     doc.get("timestamp", datetime.utcnow()),
                "embedding":     doc.get("embedding", [0.0] * 768),
            },
        }
        for doc in collection.find({})
    ]

    if actions:
        success, _ = bulk(opensearch_client, actions, request_timeout=60)
        print(f"[feedback_logs] {success}건 전송 완료")
    else:
        print("[feedback_logs] 전송할 문서가 없습니다.")
