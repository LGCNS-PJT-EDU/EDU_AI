from datetime import datetime
from opensearchpy import OpenSearch
import random

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
)

user_ids = [f"user_{i}" for i in range(1, 8)]
subjects = ["math", "cs", "law"]

for user in user_ids:
    doc = {
        "user_id": user,
        "subject": random.choice(subjects),
        "score": random.randint(60, 100),
        "level": random.choice(["novice", "intermediate", "expert"]),
        "timestamp": datetime.utcnow().isoformat()
    }
    client.index(index="post_result_logs", body=doc)

print("✅ 삽입 완료: post_result_logs")
