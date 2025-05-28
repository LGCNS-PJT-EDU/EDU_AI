from .chromadb_client import ChromaClient
from .mongodb import MongoDBClient
from .openai_client import OpenAiClient


ai_client = OpenAiClient()

chroma_client = ChromaClient(
    persist_directory="chroma_store/recommend_contents",
    openai_api_key=None
)

mongo_client  = MongoDBClient()