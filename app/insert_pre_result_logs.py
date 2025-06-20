# app/insert_pre_result_logs.py

from datetime import datetime, timedelta
from random import randint, choice
from opensearchpy import OpenSearch, helpers

# ✅ OpenSearch 클라이언트 설정
client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),  # 기본 인증 정보 (수정 가능)
    use_ssl=False,
    verify_certs=False
)

# ✅ 샘플 유저 ID와 과목, 레벨
user_ids = [f"user_{i:03d}" for i in range(1, 8)]
subjects = ["math", "cs", "law"]
levels = ["novice", "amateur", "intermediate", "expert", "master"]

# ✅ 샘플 도큐먼트 리스트 생성
docs = []
for user_id in user_ids:
    doc = {
        "_index": "pre_result_logs",
        "_source": {
            "user_id": user_id,
            "subject": choice(subjects),
            "score": randint(40, 95),
            "level": choice(levels),
            "timestamp": (datetime.utcnow() - timedelta(days=randint(0, 5))).isoformat()
        }
    }
    docs.append(doc)

# ✅ OpenSearch에 Bulk 삽입
success, _ = helpers.bulk(client, docs)
print(f"✅ 삽입 완료: {success}건 pre_result_logs에 입력됨")
