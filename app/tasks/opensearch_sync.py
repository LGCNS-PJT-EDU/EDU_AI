from celery import shared_task
from opensearchpy.helpers import bulk
from datetime import datetime
from app.clients.opensearch_client import client as es  # 클라이언트 경로 맞춰주세요!
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongo = MongoClient(os.getenv("MONGO_DB_URL"))
collection = mongo["ai_interview"]["interview_contents"]

@shared_task
def sync_feedback_logs_to_opensearch():
    cursor = collection.find()
    actions = []
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
        success, _ = bulk(es, actions)
        print(f"총 {success}개 문서 전송됨")
    else:
        print("MongoDB에서 읽은 문서가 없습니다!")

if __name__ == "__main__":
    sync_feedback_logs_to_opensearch()
