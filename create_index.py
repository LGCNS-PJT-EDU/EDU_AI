from opensearchpy import OpenSearch

client = OpenSearch("http://localhost:9200")

index_name = "feedback_logs"

mapping = {
    "mappings": {
        "properties": {
            "user_id": {"type": "keyword"},
            "feedback_type": {"type": "keyword"},
            "subject": {"type": "keyword"},
            "final_comment": {"type": "text"},  # <- 수정됨
            "score": {"type": "integer"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 768
            },
            "timestamp": {"type": "date"}
        }
    }
}

# 인덱스가 이미 있으면 삭제 후 생성
if client.indices.exists(index=index_name):
    client.indices.delete(index=index_name)

response = client.indices.create(index=index_name, body=mapping)
print("Index created:", response)
