from fastapi import APIRouter, HTTPException, Response

from app.clients import db_clients
from typing import List

from app.models.pre_assessment.request import AssessmentResult
from app.models.pre_assessment.response import QuestionStructure
from app.services.assessment.common import result_generate, safe_sample
from app.services.assessment.post import generate_key
from app.services.assessment.pre import level_to_string
from app.services.common.common import subject_id_to_name, get_user

router = APIRouter()

question_db = db_clients["ai_platform"]
assessment_db = db_clients["assessment"]
user_db = db_clients["user"]

@router.get("/subject", response_model=List[QuestionStructure], response_model_by_alias=False, summary="사후 평가 문제를 생성", description="데이터베이스에서 사전에 지정된 규칙에 따라 저장된 문제를 가져오고, 사전 평가 문제 데이터셋을 완성한다.")
async def get_pretest(user_id:str, subject_id: int):
    user = await get_user(user_id)

    tmp = user.get("level", {})
    level = tmp.get(str(subject_id))

    subject_name = await subject_id_to_name(subject_id)

    question_count = {}
    if level == "novice":
        question_count = {"high": 0, "medium": 1, "low": 2}
    elif level == "amateur":
        question_count = {"high": 0, "medium": 2, "low": 1}
    elif level == "intermediate":
        question_count = {"high": 1, "medium": 1, "low": 1}
    elif level == "expert":
        question_count = {"high": 2, "medium": 1, "low": 0}
    elif level == "master":
        question_count = {"high": 3, "medium": 0, "low": 0}
    else:
        raise HTTPException(status_code=500, detail="Forbidden attempt occurred")

    all_questions = await question_db.db[subject_name].find().to_list(length=1000)

    selected: List[QuestionStructure] = []
    for chapter_num in range(1, 6):
        chapter_questions = [q for q in all_questions if q.get("chapterNum") == chapter_num]

        hard_qs = [q for q in chapter_questions if q.get("difficulty") == "high"]
        mid_qs = [q for q in chapter_questions if q.get("difficulty") == "medium"]
        easy_qs = [q for q in chapter_questions if q.get("difficulty") == "low"]

        selected += safe_sample(hard_qs, question_count["high"])
        selected += safe_sample(mid_qs, question_count["medium"])
        selected += safe_sample(easy_qs, question_count["low"])

    result = result_generate(selected)
    return result


@router.post('/subject', summary="사용자의 사후 평가 결과를 저장", description="백엔드 서버에서 전송된 사용자의 사후 평가 결과를 데이터베이스에 저장한다.")
async def save_result(user_id: str, payload: AssessmentResult):
    user = await get_user(user_id)
    compiled_data = payload.model_dump(exclude={"userId"})
    level = await level_to_string(payload.subject.level)
    level_key = str(payload.subject.subjectId)

    new_key = await generate_key(user)
    await assessment_db.post_result.update_one(
        {
            "userId": user["user_id"],
        },
        {
            "$set": {
                new_key: compiled_data
            }
        },
        upsert=True
    )

    await user_db.user_profile.update_one(
        {
            "user_id": user["user_id"],
        },
        {
            "$set": {
                f"level.{level_key}": level
            }
        },
        upsert=True
    )

    return Response(status_code=204)