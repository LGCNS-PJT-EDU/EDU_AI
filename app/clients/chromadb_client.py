import os
from dotenv import load_dotenv
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from chromadb.config import Settings

load_dotenv()

class ChromaClient:
    def __init__(self, persist_directory: str = "chroma_store/contents", openai_api_key: str | None = None):
        key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not found")

        self.embedding = OpenAIEmbeddings(openai_api_key=key)
        self.client = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embedding,
            client_settings=Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=os.getenv("CHROMA_DB_HOST", "localhost"),
                chroma_server_http_port=int(os.getenv("CHROMA_DB_PORT", 8000))
            )
        )

    def similarity_search_with_score(self, query: str, k: int = 6):
        return self.client.similarity_search_with_score(query, k)

    def similarity_search(self, query: str, k: int = 6, metadata_filter=None):
        return self.client.similarity_search(query, k, filter=metadata_filter)

    def add_documents(self, docs: List[Document]):
        self.client.add_documents(documents=docs)

    def count_documents(self):
        return self.client._collection.count()

    def get_documents_by_user(self, user_id: str, limit: int = 5):
        return self.client._collection.get(where={"user_id": user_id})

    def delete_documents(self, user_id: str = None, source: str = None):
        filter_ = {}
        if user_id:
            filter_["user_id"] = user_id
        if source:
            filter_["source"] = source
        if not filter_:
            print(" 삭제 조건이 없습니다.")
            return
        result = self.client._collection.delete(where=filter_)
        print(f" 삭제 완료: {filter_} → {result}")
