from .chromadb_client import ChromaClient
from .mongodb import MongoClientsManager  # ✅ MongoClientsManager만 사용
from .openai_client import OpenAiClient

# 클라이언트 초기화
ai_client = OpenAiClient()

chroma_client = ChromaClient(
    persist_directory="chroma_store/recommend_contents",
    openai_api_key=None
)

# MongoClientsManager 사용
db_clients = MongoClientsManager()
