from celery import shared_task
from opensearchpy.helpers import bulk
from datetime import datetime
from app.clients.opensearch_client import opensearch_client  # ← 여기!
from app.clients.mongodb import db_client   # ← 여기!

mongo_client = db_client()
collection = mongo_client.feedback  # ai_platform.feedback 컬렉션

@shared_task
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
                    "embedding": doc.get("embedding", [0.0] * 768)
                }
            })
    asyncio.run(prepare_docs())

    if actions:
        success, _ = bulk(opensearch_client, actions)
        print(f"OpenSearch 전송 완료: {success}개 문서")
    else:
        print("MongoDB에서 읽은 문서가 없습니다!")
