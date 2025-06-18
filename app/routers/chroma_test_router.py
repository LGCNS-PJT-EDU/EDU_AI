# app/routers/chroma_test_router.py

from fastapi import APIRouter
from app.utils.embed import embed_to_chroma  # 또는 필요한 모듈

router = APIRouter()

@router.post("/chroma/test-insert", summary="문서 삽입 테스트 (동기)")
async def test_insert_to_chroma(user_id: str, content: str, source_id: str):
    result = embed_to_chroma(
        user_id=user_id,
        content=content,
        source="feedback",
        source_id=source_id
    )
    return {"message": "동기 문서 삽입 완료", "result": result}
