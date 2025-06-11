# app/routers/chroma_status_router.py

from fastapi import APIRouter, HTTPException, Query
from app.clients.chromadb_client import ChromaClient
from datetime import datetime

router = APIRouter()
client = ChromaClient()

@router.get("/count", summary="전체 문서 수 확인", tags=["ChromaDB 상태 점검 API"])
async def get_total_doc_count():
    try:
        return {"total_documents": client.count_documents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/docs/user", summary="user_id 기준 문서 미리보기", tags=["ChromaDB 상태 점검 API"])
async def get_docs_by_user(user_id: str, limit: int = 5):
    try:
        results = client.get_documents_by_user(user_id=user_id, limit=limit)
        return {
            "total": len(results["ids"]),
            "samples": [
                {
                    "id": results["ids"][i],
                    "content": results["documents"][i][:100],
                    "metadata": results["metadatas"][i]
                } for i in range(min(limit, len(results["ids"])))
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"조회 오류: {str(e)}")

