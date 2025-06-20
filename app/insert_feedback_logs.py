from datetime import datetime
from opensearchpy import OpenSearch
import random

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False
)

user_ids = [f"user_{i}" for i in range(1, 8)]
subjects = ["math", "cs", "physics", "bio"]
feedback_types = ["PRE", "POST"]
comments = [
    "개념 이해가 잘 되어 있습니다.",
    "약간의 복습이 필요합니다.",
    "용어 사용이 매우 정확합니다.",
    "응답이 다소 모호했습니다.",
    "전반적으로 향상된 모습입니다.",
    "핵심 개념에 대한 이해가 부족합니다.",
    "예시 사용이 효과적이었습니다.",
    "개념 연결 능력이 향상되었습니다."
]

docs = []

for uid in user_ids:
    for _ in range(3):  # 각 사용자당 피드백 3개
        doc = {
            "user_id": uid,
            "subject": random.choice(subjects),
            "feedback_type": random.choice(feedback_types),
            "score": random.randint(60, 100),
            "final_comment": random.choice(comments),
            "timestamp": datetime.utcnow().isoformat()
        }
        docs.append({"index": {"_index": "feedback_logs"}})
        docs.append(doc)

response = client.bulk(body=docs)

if not response["errors"]:
    print("✅ 피드백 데이터 삽입 완료")
else:
    print("❌ 삽입 중 오류 발생:", response)
