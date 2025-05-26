import os

from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

load_dotenv()

class ChromaClient:
    def __init__(self, persist_directory: str = "chroma_store/contents", openai_api_key: str | None = None):
        key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not found")

        self.embedding = OpenAIEmbeddings(openai_api_key=key)

        self.client = Chroma(
            persist_directory=persist_directory,
            embedding_function=self.embedding
        )

    def similarity_search_with_score(self, query: str, k: int = 6):
        return self.client.similarity_search_with_score(query, k)