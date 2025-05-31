import os

from chromadb.config import Settings
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from typing import List


load_dotenv()

class ChromaClient:
    def __init__(self, persist_directory: str = "chroma_store/contents", openai_api_key: str | None = None):
        key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not found")

        self.embedding = OpenAIEmbeddings(openai_api_key=key)

        settings = Settings(
            chroma_api_impl="chromadb.api.fastapi.FastAPI",
            chroma_server_host=os.getenv("CHROMA_DB_HOST"),
            chroma_server_http_port=int(os.getenv("CHROMA_DB_PORT")),
        )

        self.settings = settings

        self.client = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embedding,
            client_settings=settings
        )

    def similarity_search_with_score(self, query: str, k: int = 6):
        return self.client.similarity_search_with_score(query, k)

    def similarity_search(self, query: str, k: int = 6):
        return self.similarity_search_with_score(query, k)

    def add_documents(self, docs: List[Document]):
        """외부에서 문서 삽입을 쉽게 호출할 수 있도록 래핑"""
        self.client.add_documents(docs)

