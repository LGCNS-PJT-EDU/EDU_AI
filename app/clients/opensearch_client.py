# app/clients/opensearch_client.py
from opensearchpy import OpenSearch
import os

def get_opensearch_client():
    return OpenSearch(
        hosts=[{"host": os.getenv("OPENSEARCH_HOST", "localhost"), "port": int(os.getenv("OPENSEARCH_PORT", 9200))}],
        http_auth=(os.getenv("OPENSEARCH_USER", "admin"), os.getenv("OPENSEARCH_PASS", "admin")),
        use_ssl=False,
        verify_certs=False
    )

# 기본 객체도 생성해둠 (기본 사용 용도)
opensearch_client = get_opensearch_client()
