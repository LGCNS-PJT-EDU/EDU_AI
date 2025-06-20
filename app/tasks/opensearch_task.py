# app/tasks/opensearch_task.py
from celery import shared_task
from datetime import datetime
from pymongo import MongoClient
from opensearchpy.helpers import bulk
from dateutil.parser import parse as parse_date
from app.clients.opensearch_client import get_opensearch_client
opensearch_client = get_opensearch_client()# PyMongo 동기 래퍼

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
        actions = []
        for doc in collection.find({}):
            timestamp = doc.get("timestamp")
            if isinstance(timestamp, str):
                try:
                    timestamp = parse_date(timestamp)
                except Exception:
                    timestamp = datetime.utcnow()
            elif not timestamp:
                timestamp = datetime.utcnow()

            action = {
                "_index": index_name,
                "_id": str(doc["_id"]),
                "_source": {
                    **{k: v for k, v in doc.items() if k != "_id"},
                    "timestamp": timestamp
                }
            }
            actions.append(action)

        if actions:
            success, _ = bulk(opensearch_client, actions, request_timeout=60)
            print(f"[{index_name}] {success}건 전송 완료")
        else:
            print(f"[{index_name}] 전송할 문서 없음")
