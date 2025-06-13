# app/utils/embed.py
from langchain_core.documents import Document
from app.clients.chromadb_client import ChromaClient
from datetime import datetime

chroma_client = ChromaClient()

def embed_to_chroma(user_id: str, content: str, source: str, source_id: str, metadata: dict = None):
    if not content:
        return

    base_meta = {
        "user_id": user_id,
        "source": source,
        "source_id": source_id,
        "inserted_at": datetime.utcnow().isoformat()
    }
    if metadata:
        base_meta.update(metadata)

    doc = Document(
        page_content=content,
        metadata=base_meta
    )
    chroma_client.add_documents([doc])
    print(f" Chroma에 삽입 완료: {source} - {source_id}")
