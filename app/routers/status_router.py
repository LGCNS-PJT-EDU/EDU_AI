# app/routers/status_router.py
from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/status", summary="서비스 헬스 체크", tags=["AIOps 상태 모니터링"])
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "RAG 기반 학습 플랫폼",
        "message": "서비스가 정상적으로 작동 중입니다."
    }
