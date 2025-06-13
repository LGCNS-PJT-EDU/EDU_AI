#  chroma_status_router.py (라우터)

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


@router.delete("/docs/delete", summary="user_id + source 기준 문서 삭제")
async def delete_documents_by_user_and_source(
    user_id: str = Query(..., description="사용자 ID"),
    source: str = Query(..., description="문서 출처 예: feedback, recommendation"),
    limit: Optional[int] = Query(default=None, description="최대 삭제 문서 수 (기본: 전체)"),
    sort_order: Optional[str] = Query(default="asc", pattern="^(asc|desc)$", description="정렬 기준 (asc: 오래된 순, desc: 최신 순)")
):
    try:
        deleted_ids = client.delete_documents(
            user_id=user_id,
            source=source,
            limit=limit,
            sort_order=sort_order
        )
        delete_total.labels(status="success", source=source).inc()
        if deleted_ids:
            return {"message": f"삭제 성공: {len(deleted_ids)}개 삭제됨", "deleted_ids": deleted_ids}
        else:
            return {"message": "조건에 해당하는 문서가 없습니다."}
    except Exception as e:
        delete_total.labels(status="error", source=source).inc()
        raise HTTPException(status_code=500, detail=f"삭제 오류: {str(e)}")

@router.get("/count", summary="전체 문서 수 확인", tags=["ChromaDB 상태 점검 API"])
async def get_total_doc_count():
    try:
        return {"total_documents": client.count_documents()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/docs/delete", summary="user_id + source 기준 문서 삭제", tags=["ChromaDB 상태 점검 API"])
async def delete_documents_by_user_and_source(
    user_id: str = Query(..., description="사용자 ID"),
    source: str = Query(..., description="문서 출처 예: feedback, recommendation"),
    limit: Optional[int] = Query(None, description="최대 삭제 문서 수 (기본: 전체)"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="정렬 기준 (asc: 오래된 순, desc: 최신 순)")
):
    try:
        deleted_ids = client.delete_documents(
            user_id=user_id,
            source=source,
            limit=limit,
            sort_order=sort_order
        )

        delete_total.labels(status="success", source=source).inc()

        return {
            "message": f"{len(deleted_ids)}개 문서 삭제 완료",
            "deleted_ids": deleted_ids
        }
    except Exception as e:
        delete_total.labels(status="error", source=source).inc()
        raise HTTPException(status_code=500, detail=f"삭제 오류: {str(e)}")




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
