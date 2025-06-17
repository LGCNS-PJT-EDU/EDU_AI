from opensearchpy import OpenSearch
client = OpenSearch("http://localhost:9200")
print(client.count(index="feedback_logs"))

