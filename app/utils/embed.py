# app/utils/embed.py
from langchain_core.documents import Document
from app.clients.chromadb_client import ChromaClient
from datetime import datetime, date
from app.utils.prometheus_metrics import daily_insert_total

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

    doc = Document(page_content=content, metadata=base_meta)
    chroma_client.add_documents([doc])

    daily_insert_total.labels(source=source, date=str(date.today())).inc()
    print(f" Chroma에 삽입 완료: {source} - {source_id}")

    return {"message": f"{source} - {source_id} 삽입 완료"}
