# app/routes/post_assessment.py

from fastapi import APIRouter

router = APIRouter()

@router.post("/submit-assessment")
async def submit_post_assessment():
    return {"message": "사후 평가 저장"}

