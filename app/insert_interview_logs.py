from datetime import datetime
from opensearchpy import OpenSearch
import random

client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
)

user_ids = [f"user_{i}" for i in range(1, 8)]
questions = [
    ("Q1", "Explain the concept of recursion."),
    ("Q2", "What is normalization in databases?"),
    ("Q3", "Define polymorphism in OOP.")
]

for user in user_ids:
    qid, question = random.choice(questions)
    doc = {
        "user_id": user,
        "question_id": qid,
        "question": question,
        "answer": "Sample answer...",
        "evaluation": {
            "logic": random.randint(1, 5),
            "accuracy": random.randint(1, 5),
            "clarity": random.randint(1, 5),
            "terms": random.randint(1, 5),
            "overall_comment": "Well explained" if random.random() > 0.5 else "Needs improvement"
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    client.index(index="interview_logs", body=doc)

print("✅ 삽입 완료: interview_logs")
