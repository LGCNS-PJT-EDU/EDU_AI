from fastapi import APIRouter, HTTPException, Response

from app.clients import db_clients
from typing import List

from app.models.pre_assessment.request import AssessmentResult
from app.models.pre_assessment.response import QuestionStructure
from app.services.assessment.common import result_generate, safe_sample
from app.services.assessment.post import generate_key
from app.services.assessment.pre import level_to_string
from app.services.common.common import subject_id_to_name, get_user
from app.utils.embed import embed_to_chroma

router = APIRouter()

@router.get("/subject", response_model=List[QuestionStructure], response_model_by_alias=False)
async def get_posttest(user_id: str, subject_id: int):
    user = await get_user(user_id)

    level = user.get("level", {}).get(str(subject_id))
    if not level:
        raise HTTPException(status_code=500, detail="Forbidden attempt occurred")

    subject_name = await subject_id_to_name(subject_id)
    all_questions = await db_clients.questions.find().to_list(length=1000)

    question_count = {
        "novice": {"high": 0, "medium": 1, "low": 2},
        "amateur": {"high": 0, "medium": 2, "low": 1},
        "intermediate": {"high": 1, "medium": 1, "low": 1},
        "expert": {"high": 2, "medium": 1, "low": 0},
        "master": {"high": 3, "medium": 0, "low": 0}
    }.get(level)

    if not question_count:
        raise HTTPException(status_code=500, detail="Forbidden attempt occurred")

    selected: List[QuestionStructure] = []
    for chapter_num in range(1, 6):
        chapter_questions = [q for q in all_questions if q.get("chapterNum") == chapter_num]

        hard_qs = [q for q in chapter_questions if q.get("difficulty") == "high"]
        mid_qs = [q for q in chapter_questions if q.get("difficulty") == "medium"]
        easy_qs = [q for q in chapter_questions if q.get("difficulty") == "low"]

        selected += safe_sample(hard_qs, question_count["high"])
        selected += safe_sample(mid_qs, question_count["medium"])
        selected += safe_sample(easy_qs, question_count["low"])

    return result_generate(selected)


@router.post("/subject")
async def save_result(user_id: str, payload: AssessmentResult):
    user = await get_user(user_id)
    compiled_data = payload.model_dump(exclude={"userId"})
    level_key = str(payload.subject.subjectId)
    level = await level_to_string(payload.subject.level)

    for ch in compiled_data.get("chapters", []):
        embed_to_chroma(user_id=user_id, content=ch.get("userAnswer", ""), source="post_result", source_id=str(ch.get("questionId")))

    new_key = await generate_key(user)
    await db_clients.post_result.update_one(
        {"userId": user["user_id"]},
        {"$set": {new_key: compiled_data}},
        upsert=True
    )

    await db_clients.user_profile.update_one(
        {"user_id": user["user_id"]},
        {"$set": {f"level.{level_key}": level}},
        upsert=True
    )

    return Response(status_code=204)