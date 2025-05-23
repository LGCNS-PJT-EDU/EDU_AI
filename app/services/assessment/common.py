import random
from typing import List

from fastapi import HTTPException

from app.clients.mongodb import db
from app.models.pre_assessment.response import QuestionStructure


async def get_user(user_id):
    user = await db.user_profiles.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def safe_sample(pool, cnt):
    if len(pool) < cnt:
        raise HTTPException(
            status_code=500,
            detail=f"Not enough questions: required {cnt}, got {len(pool)}"
        )
    return random.sample(pool, cnt)


def result_generate(question_list):
    random.shuffle(question_list)

    result: List[QuestionStructure] = []
    for idx, doc in enumerate(question_list, start=1):
        doc.pop("_id", None)
        doc["question_id"] = idx
        result.append(QuestionStructure(**doc))

    return result