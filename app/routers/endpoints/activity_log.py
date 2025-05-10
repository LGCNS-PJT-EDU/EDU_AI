# app/routers/activity_log.py

from fastapi import APIRouter

router = APIRouter()

@router.post("/log-activity")
async def log_learning_activity():
    return {"message": "활동 기록 저장"}
