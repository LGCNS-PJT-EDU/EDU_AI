import random
from typing import List

from fastapi import HTTPException

from app.clients.mongodb import db
from app.models.pre_assessment.response import PreQuestion


async def get_user(user_id):
    user = await db.user_profiles.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def subject_id_to_name(subject_id):
    tech_map = await db.techMap.find_one({})
    if not tech_map:
        raise HTTPException(status_code=404, detail="Can't find data")
    subject_name = tech_map.get(str(subject_id))
    if not subject_name:
        raise HTTPException(status_code=404, detail="Such subject not exist")
    return subject_name


def safe_sample(pool, cnt):
    if len(pool) < cnt:
        raise HTTPException(
            status_code=500,
            detail=f"Not enough questions: required {cnt}, got {len(pool)}"
        )
    return random.sample(pool, cnt)


def result_generate(question_list):
    random.shuffle(question_list)

    # 5) question_id 부여 및 모델 변환
    result: List[PreQuestion] = []
    for idx, doc in enumerate(question_list, start=1):
        doc.pop("_id", None)
        doc["question_id"] = idx
        result.append(PreQuestion(**doc))

    return result