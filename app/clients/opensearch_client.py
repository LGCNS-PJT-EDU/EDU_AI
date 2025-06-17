from opensearchpy import OpenSearch
import os

opensearch_client = OpenSearch(
    hosts=[os.getenv("OPENSEARCH_HOST", "http://localhost:9200")],
    http_auth=(os.getenv("OPENSEARCH_USER", "admin"), os.getenv("OPENSEARCH_PASSWORD", "admin")),
    use_ssl=False,
    verify_certs=False
)
