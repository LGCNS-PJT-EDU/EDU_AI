# app/tasks/opensearch_task.py
# app/tasks/opensearch_task.py
from celery import shared_task
from datetime import datetime
from pymongo import MongoClient              # Motor → PyMongo
from opensearchpy.helpers import bulk
from app.clients.opensearch_client import opensearch_client  # PyMongo 동기 래퍼

mongo = MongoClient("mongodb://54.180.4.224:27017")

COLLECTION_MAPPINGS = {
    "interview_logs":      mongo["ai_interview"]["interview_contents"],
    "recommendation_logs": mongo["ai_platform"]["recommend_cache"],
    "feedback_logs":       mongo["feedback"]["feedback_content"],
    "startup_logs":        mongo["local"]["startup_log"],
    "pre_result_logs":     mongo["assessment"]["pre_result"],
    "post_result_logs":    mongo["assessment"]["post_result"],
}

@shared_task(name="sync_all_logs_to_opensearch")
def sync_all_logs_to_opensearch():
    for index_name, collection in COLLECTION_MAPPINGS.items():
        actions = [
            {
                "_index": index_name,
                "_id": str(doc["_id"]),
                "_source": {
                    **{k: v for k, v in doc.items() if k != "_id"},
                    "timestamp": doc.get("timestamp", datetime.utcnow())
                }
            }
            for doc in collection.find({})
        ]

        if actions:
            success, _ = bulk(opensearch_client, actions, request_timeout=60)
            print(f"[{index_name}] {success}건 전송 완료")
        else:
            print(f"[{index_name}] 전송할 문서 없음")
