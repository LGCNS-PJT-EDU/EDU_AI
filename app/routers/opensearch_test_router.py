# app/routers/opensearch_test_router.py

from fastapi import APIRouter
from app.tasks.opensearch_task import sync_all_logs_to_opensearch

router = APIRouter()

@router.post("/opensearch/test-sync", summary="모든 Mongo 로그 → OpenSearch 전송")
async def test_opensearch_sync():
    sync_all_logs_to_opensearch.delay()
    return {"message": "전송 요청 완료됨 (Celery 실행됨)"}
