# routers/chroma_router.py

from fastapi import APIRouter
from app.clients.chromadb_client import ChromaClient

router = APIRouter()
client = ChromaClient()

@router.delete("/delete-all-docs")  # 이미 /api/chroma 로 prefix 붙기 때문에 여기선 짧게
def delete_all_docs():
    count = client.delete_all_documents()

    return {"message": "전체 문서 삭제 완료", "deleted_count": count}