import os
from dotenv import load_dotenv
from typing import List, Optional
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
        self.collection = self.client._collection

    def similarity_search_with_score(self, query: str, k: int = 6):
        return self.client.similarity_search_with_score(query, k)

    def similarity_search(self, query: str, k: int = 6, metadata_filter=None):
        return self.client.similarity_search(query, k, filter=metadata_filter)

    def add_documents(self, docs: List[Document]):
        self.client.add_documents(documents=docs)

    def count_documents(self):
        return self.collection.count()

    def get_documents_by_user(self, user_id: str, limit: int = 5):
        return self.collection.get(where={"user_id": user_id}, limit=limit)

    def delete_documents(self, user_id: str = None, source: str = None, limit: Optional[int] = None, sort_order: Optional[str] = "asc"):
        filter_ = []
        if user_id:
            filter_.append({"user_id": user_id})
        if source:
            filter_.append({"source": source})

        if not filter_:
            print("\n삭제 조건이 없습니다.")
            return

        # 수정: Mongo 스타일 → Chroma 스타일 where_clause로 변환
        where_clause = {k: v for d in filter_ for k, v in d.items()}

        if limit:
            docs = self.collection.get(where=where_clause)
            docs_with_created_at = list(zip(docs["ids"], docs["metadatas"]))
            sorted_docs = sorted(
                docs_with_created_at,
                key=lambda x: x[1].get("created_at", "9999-99-99T99:99:99"),
                reverse=(sort_order == "desc")
            )
            ids_to_delete = [doc[0] for doc in sorted_docs[:limit]]
            if not ids_to_delete:
                print("\n삭제할 문서가 없습니다.")
                return
            result = self.collection.delete(ids=ids_to_delete)
            print(f"\n[선택 삭제] ID 기준 {len(ids_to_delete)}개 삭제 → {result}")
            return ids_to_delete
        else:
            result = self.collection.delete(where=where_clause)
            print(f"\n[전체 삭제] 조건 {where_clause} → {result}")
            return []

    def delete_all_documents(self, batch_size: int = 500):
        """컬렉션 내 모든 문서를 batch로 나눠 삭제합니다 (컬렉션은 유지)."""
        all_docs = self.collection.get()
        all_ids = all_docs.get("ids", [])

        if not all_ids:
            print("\n[전체 삭제] 삭제할 문서가 없습니다.")
            return

        total = len(all_ids)
        print(f"\n[전체 삭제] 총 {total}개 문서 삭제 시작")

        for i in range(0, total, batch_size):
            batch_ids = all_ids[i:i + batch_size]
            result = self.collection.delete(ids=batch_ids)
            print(f"  → {i + 1} ~ {i + len(batch_ids)}번 문서 삭제 완료")

        print(f"\n 전체 {total}개 문서 삭제 완료")
        return total


if __name__ == "__main__":
    chroma = ChromaClient()
    chroma.delete_all_documents()
