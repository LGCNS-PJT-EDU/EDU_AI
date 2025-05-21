from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from app.clients.mongodb import db
from datetime import datetime
from typing import List
import random

from app.models.pre_assessment.request import AssessmentResult
from app.models.pre_assessment.response import QuestionStructure
from app.routers.pre_assessment_router import AnswerItem, calculate_pretest_score
from app.services.assessment.common import get_user, subject_id_to_name, result_generate, safe_sample
from app.services.assessment.post import generate_key

router = APIRouter()

@router.get("/subject", response_model=List[QuestionStructure], response_model_by_alias=False, summary="사후 평가 문제를 생성", description="데이터베이스에서 사전에 지정된 규칙에 따라 저장된 문제를 가져오고, 사전 평가 문제 데이터셋을 완성한다.")
async def get_pretest(user_id:str, subject_id: int):
    user = await get_user(user_id)
    level = user.get("level")

    subject_name = await subject_id_to_name(subject_id)

    question_count = {}
    if level == "low":
        question_count["high"], question_count["medium"], question_count["low"] = 2, 4, 9
    elif level == "medium":
        question_count["high"], question_count["medium"], question_count["low"] = 5, 5, 5
    elif level == "high":
        question_count["high"], question_count["medium"], question_count["low"] = 7, 6, 2
    else:
        raise HTTPException(status_code=500, detail="Forbidden attempt occurred")

    all_questions = await db[subject_name].find().to_list(length=1000)

    hard_qs = [q for q in all_questions if q["difficulty"] == "high"]
    mid_qs = [q for q in all_questions if q["difficulty"] == "medium"]
    easy_qs = [q for q in all_questions if q["difficulty"] == "low"]

    selected = []
    selected += safe_sample(hard_qs, question_count["high"])
    selected += safe_sample(mid_qs,  question_count["medium"])
    selected += safe_sample(easy_qs, question_count["low"])

    result = result_generate(selected)
    return result


@router.post('/subject', summary="사용자의 사후 평가 결과를 저장", description="백엔드 서버에서 전송된 사용자의 사후 평가 결과를 데이터베이스에 저장한다.")
async def save_result(user_id: str, payload: AssessmentResult):
    user = await get_user(user_id)
    compiled_data = payload.model_dump(exclude={"userId"})

    new_key = await generate_key(user)

    await db.user_profiles.update_one(
        {"user_id": user["user_id"]},
        {"$set": { new_key: compiled_data }}
    )
    return Response(status_code=204)