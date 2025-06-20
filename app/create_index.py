from opensearchpy import OpenSearch

# OpenSearch 연결 설정
client = OpenSearch(
    hosts=[{"host": "localhost", "port": 9200}],
    http_auth=("admin", "admin"),
    use_ssl=False,
    verify_certs=False
)

# 인덱스 매핑 정의
def get_index_mappings():
    return {
        "feedback_logs": {
            "properties": {
                "user_id": {"type": "keyword"},
                "feedback_type": {"type": "keyword"},
                "subject": {"type": "keyword"},
                "final_comment": {
                    "type": "text",
                    "fields": {
                        "keyword": {"type": "keyword"}
                    }
                },
                "score": {"type": "integer"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": 768
                },
                "timestamp": {"type": "date"}
            }
        },
        "interview_logs": {
    "properties": {
        "user_id": {"type": "keyword"},
        "question_id": {"type": "keyword"},
        "question": {"type": "text"},
        "answer": {"type": "text"},
        "logic": {"type": "integer"},
        "accuracy": {"type": "integer"},
        "clarity": {"type": "integer"},
        "terms": {"type": "integer"},
        "overall_comment": {
            "type": "text",
            "fields": {"keyword": {"type": "keyword"}}
        },
        "timestamp": {"type": "date"}
    }
},
        "recommendation_logs": {
            "properties": {
                "user_id": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "user_context": {"type": "text"},
                "timestamp": {"type": "date"}
            }
        },
        "startup_logs": {
            "properties": {
                "service": {"type": "keyword"},
                "message": {"type": "text"},
                "timestamp": {"type": "date"}
            }
        },
        "pre_result_logs": {
            "properties": {
                "user_id": {"type": "keyword"},
                "subject": {"type": "keyword"},
                "score": {"type": "integer"},
                "level": {"type": "keyword"},
                "timestamp": {"type": "date"}
            }
        },
        "post_result_logs": {
            "properties": {
                "user_id": {"type": "keyword"},
                "subject": {"type": "keyword"},
                "score": {"type": "integer"},
                "level": {"type": "keyword"},
                "timestamp": {"type": "date"}
            }
        }
    }

# 인덱스 재생성
index_mappings = get_index_mappings()
for index_name, mapping in index_mappings.items():
    if client.indices.exists(index=index_name):
        client.indices.delete(index=index_name)
        print(f"🗑️ Deleted index: {index_name}")
    client.indices.create(index=index_name, body={"mappings": mapping})
    print(f"✅ Created index: {index_name}")
