from fastapi import APIRouter, Response
from app.clients.mongodb import db
from datetime import datetime

from app.models.pre_assessment.request import AssessmentInput, AssessmentResult
from app.models.pre_assessment.response import QuestionStructure
from app.services.assessment.common import get_user, subject_id_to_name, safe_sample, result_generate
from app.utils.level_utils import calculate_level_from_answers
from typing import List

router = APIRouter()

# 사전 평가 기반 사용자 평가
@router.post("/user-assessment")
async def save_user_assessment(data: AssessmentInput):
    level = calculate_level_from_answers(data.survey_answers)

    await db.user_profiles.update_one(
        {"user_id": data.user_id},
        {"$set": {
            "survey_answers": data.survey_answers,
            "pre_test_score": data.pre_test_score,
            "calculated_level": level
        }},
        upsert=True
    )
    return {"success": True, "calculated_level": level}

# 사전 평가 로그용 빌더 함수
def build_pretest_log(user_id: str, questions: list[dict]):
    return {
        "user_id": user_id,
        "questions": [
            {
                "question_id": q["question_id"],
                "difficulty": q["difficulty"],
                "track": q["track"],
                "level": q["level"]
            }
            for q in questions
        ],
        "timestamp": datetime.now().isoformat()
    }


@router.get("/subject", response_model=List[QuestionStructure], response_model_by_alias=False, summary="사전 평가 문제를 생성", description="데이터베이스에서 사전에 지정된 규칙에 따라 저장된 문제를 가져오고, 사전 평가 문제 데이터셋을 완성한다.")
async def get_pretest(user_id: str, subject_id: int):
    subject_name = await subject_id_to_name(subject_id)

    all_questions = await db[subject_name].find().to_list(length=1000)
    chapter_names = {q["chapterName"] for q in all_questions}

    selected = []
    for chapter in chapter_names:
        mid_qs = [q for q in all_questions if q["chapterName"] == chapter and q["difficulty"] == "medium"]
        easy_qs = [q for q in all_questions if q["chapterName"] == chapter and q["difficulty"] == "low"]

        selected += safe_sample(mid_qs, 1)
        selected += safe_sample(easy_qs, 1)

    result = result_generate(selected)
    return result


@router.post('/subject', summary="사용자의 사전 평가 결과를 저장", description="백엔드 서버에서 전송된 사용자의 사전 평가 결과를 데이터베이스에 저장한다.")
async def save_result(user_id: str, payload: AssessmentResult):
    user = await get_user(user_id)
    compiled_data = payload.model_dump(exclude={"userId"})

    await db.user_profiles.update_one(
        {"user_id": user["user_id"]},
        {"$set": { "pre_assessment": compiled_data }}
    )
    return Response(status_code=204)