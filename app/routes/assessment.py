from fastapi import APIRouter
from pydantic import BaseModel
from app.mongodb import db
import random

router = APIRouter()

#  1. 사용자 설문 + 진단 저장
class AssessmentInput(BaseModel):
    user_id: str
    survey_answers: dict
    pre_test_score: int

@router.post("/user-assessment")
async def save_user_assessment(data: AssessmentInput):
    await db.user_profiles.update_one(
        {"user_id": data.user_id},
        {"$set": {
            "survey_answers": data.survey_answers,
            "pre_test_score": data.pre_test_score
        }},
        upsert=True
    )
    return {"success": True}

#  2. 문제 랜덤 추출
@router.get("/get-pretest")
async def get_pretest():
    cursor = db.evaluation_questions.find({"type": "pre"})
    questions = await cursor.to_list(length=1000)
    if len(questions) < 10:
        return {"error": "Not enough pre-test questions in DB."}
    selected = random.sample(questions, 10)
    return {"questions": selected}


@router.get("/get-posttest")
async def get_posttest():
    cursor = db.evaluation_questions.find({"type": "post"})
    questions = await cursor.to_list(length=1000)
    if len(questions) < 15:
        return {"error": "Not enough post-test questions in DB."}
    selected = random.sample(questions, 15)
    return {"questions": selected}
