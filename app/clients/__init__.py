from .chromadb_client import ChromaClient
from .openai_client import OpenAiClient

ai_client = OpenAiClient()
chroma_client = ChromaClient()