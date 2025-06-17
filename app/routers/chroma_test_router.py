# app/routers/chroma_test_router.py

from fastapi import APIRouter
from app.tasks.feedback_task import sync_feedback_to_chroma_task

router = APIRouter()

@router.post("/chroma/test-insert", summary="문서 삽입 테스트 (Celery)")
async def test_insert_to_chroma(user_id: str, content: str, source_id: str):
    """
    Chroma 테스트용 문서 삽입 라우터
    - Celery Task로 비동기 실행됨
    """
    sync_feedback_to_chroma_task.delay(user_id, content, source_id)
    return {"message": "비동기 문서 삽입 요청 완료 (Celery 전송됨)"}
