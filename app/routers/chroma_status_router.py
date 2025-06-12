# app/routers/chroma_status_router.py

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from enum import Enum
from app.clients.chromadb_client import ChromaClient
import prometheus_client

# Prometheus 지표 정의
delete_total = prometheus_client.Counter("chroma_doc_delete_total", "문서 삭제 요청 수", ["status", "source"])

class SourceType(str, Enum):
    recommendation = "recommendation"
    feedback = "feedback"
    interview = "interview"
    pre_evaluation = "pre_evaluation"
    post_evaluation = "post_evaluation"

router = APIRouter()
client = ChromaClient()


@router.delete("/docs/delete", summary="user_id + source 기준 문서 삭제", tags=["ChromaDB 관리 API"])
async def delete_docs(user_id: str, source: Optional[SourceType] = Query(default=None)):
    try:
        result = client.delete_documents(user_id=user_id, source=source.value if source else None)
        delete_total.labels(status="success", source=source.value if source else "all").inc()
        return {"status": "success", "deleted": result}
    except Exception as e:
        delete_total.labels(status="failure", source=source.value if source else "all").inc()
        raise HTTPException(status_code=500, detail=f"삭제 오류: {str(e)}")

@router.get("/count", summary="전체 문서 수 확인", tags=["ChromaDB 상태 점검 API"])
async def get_total_doc_count():
    try:
        return {"total_documents": client.count_documents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/docs/user", summary="user_id 기준 문서 미리보기", tags=["ChromaDB 상태 점검 API"])
async def get_docs_by_user(
    user_id: str,
    limit: int = 5,
    source: Optional[SourceType] = Query(default=None)
):
    try:
        # 모든 문서를 가져온 후 라우터에서 source 필터링
        results = client.get_documents_by_user(user_id=user_id, limit=limit)

        # source가 주어졌다면 필터링
        filtered = [
            {
                "id": results["ids"][i],
                "content": results["documents"][i][:100],
                "metadata": results["metadatas"][i]
            }
            for i in range(len(results["ids"]))
            if not source or results["metadatas"][i].get("source") == source.value
        ]

        return {
            "total": len(filtered),
            "samples": filtered[:limit]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"조회 오류: {str(e)}")


@router.get("/docs/user/source-counts", summary="user_id 기준 source별 문서 개수", tags=["ChromaDB 상태 점검 API"])
async def get_source_counts_by_user(user_id: str):
    try:
        results = client.get_documents_by_user(user_id=user_id)
        source_counts = {}
        for metadata in results.get("metadatas", []):
            s = metadata.get("source", "unknown")
            source_counts[s] = source_counts.get(s, 0) + 1
        return source_counts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"조회 오류: {str(e)}")
