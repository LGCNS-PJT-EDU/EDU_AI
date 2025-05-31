import logging
import sys

from fastapi import APIRouter, Response
from app.clients import db_clients

from app.models.pre_assessment.request import AssessmentResult
from app.models.pre_assessment.response import QuestionStructure
from app.services.assessment.common import safe_sample, result_generate
from app.services.common.common import subject_id_to_name, get_user, question_db
from typing import List

router = APIRouter()

logger = logging.getLogger("pre-assessment-router")
logger.setLevel(logging.INFO)

question_db = db_clients["ai_platform"]
assessment_db = db_clients["assessment"]
user_db = db_clients["user"]

if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)  # 터미널로 출력
    formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

@router.get("/subject", response_model=List[QuestionStructure], response_model_by_alias=False, summary="사전 평가 문제를 생성", description="데이터베이스에서 사전에 지정된 규칙에 따라 저장된 문제를 가져오고, 사전 평가 문제 데이터셋을 완성한다.")
async def get_pretest(user_id: str, subject_id: int):
    subject_name = await subject_id_to_name(subject_id)

    all_questions = await question_db.db[subject_name].find().to_list(length=1000)
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
    subject_id = compiled_data["subject"]["subjectId"]

    await assessment_db.pre_result.update_one(
        {
            "userId": user["user_id"],
            "pre_assessment.subject.subjectId": subject_id
        },
        {
            "$set": {
                "pre_assessment": compiled_data
            }
        },
        upsert=True
    )

    return Response(status_code=204)