# app/tasks/feedback_task.py

from celery import shared_task
from datetime import datetime
from app.utils.embed import embed_to_chroma

#  1. Chroma 삽입용 Task
@shared_task(name="sync_feedback_to_chroma")
def sync_feedback_to_chroma_task(user_id: str, content: str, source_id: str):
    return embed_to_chroma(
        user_id=user_id,
        content=content,
        source="feedback",
        source_id=source_id
    )


#  2. OpenSearch 로그 전송용 Task
from opensearchpy.helpers import bulk
from app.clients.opensearch_client import opensearch_client
from app.clients import db_clients

collection = db_clients.mongo_client.feedback  # db 접근 인스턴스 수정

@shared_task(name="sync_feedback_logs_to_opensearch")
def sync_feedback_logs_to_opensearch():
    import asyncio
    actions = []

    async def prepare_docs():
        cursor = collection.find({})
        async for doc in cursor:
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
                    "embedding": doc.get("embedding", [0.0]*768)
                }
            })

    asyncio.run(prepare_docs())

    if actions:
        success, _ = bulk(opensearch_client, actions)
        print(f" OpenSearch 전송 완료: {success}개 문서")
    else:
        print(" MongoDB에서 읽은 문서가 없습니다!")
