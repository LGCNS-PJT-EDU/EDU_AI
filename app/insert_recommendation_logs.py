# app/insert_recommendation_logs.py

from datetime import datetime, timedelta
from opensearchpy import OpenSearch
import random

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False
)

user_ids = [f"user_{i}" for i in range(1, 7)]
titles = ["ML 기초 책", "딥러닝 영상 강의", "GPT 논문 요약", "RAG 튜토리얼"]
contexts = ["짧은 시간", "예산 10만원 이하", "책을 선호", "실습 중심"]

docs = []

for uid in user_ids:
    for _ in range(2):
        doc = {
            "user_id": uid,
            "title": random.choice(titles),
            "user_context": random.choice(contexts),
            "timestamp": (datetime.utcnow() - timedelta(days=random.randint(0, 15))).isoformat()
        }
        docs.append({"index": {"_index": "recommendation_logs"}})
        docs.append(doc)

response = client.bulk(body=docs)

if not response["errors"]:
    print("✅ recommendation_logs 삽입 완료")
else:
    print("❌ 오류:", response)
