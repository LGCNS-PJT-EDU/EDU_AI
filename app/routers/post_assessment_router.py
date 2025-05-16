# app/routers/post_assessment_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from datetime import datetime
import random
import json

from app.clients.mongodb import db
from app.routers.pre_assessment_router import AnswerItem, calculate_pretest_score
from app.models.pre_assessment.response import PreQuestion

router = APIRouter()

# 난이도 분포 기준 불러오기 (외부 JSON 파일 사용)
with open("config/difficulty_rules.json", "r", encoding="utf-8") as f:
    DIFFICULTY_RULES = json.load(f)


# 사후 평가 문제 출제 API
@router.get("/get-posttest", response_model=List[PreQuestion])
async def get_posttest(user_id: str, subject: str):
    #  1. 사전 평가 점수 확인
    result = await db.pretest_results.find_one({"user_id": user_id})
    if not result:
        raise HTTPException(status_code=404, detail="Pretest score not found")

    score = result["score"]

    #  2. 사후 평가 난이도 규칙 (내부 JSON으로 삽입)
    difficulty_rules = [
        {
            "min": 0,
            "max": 4,
            "distribution": {"low": 10, "medium": 5}
        },
        {
            "min": 5,
            "max": 8,
            "distribution": {"low": 5, "medium": 8, "high": 2}
        },
        {
            "min": 9,
            "max": 12,
            "distribution": {"medium": 10, "high": 5}
        },
        {
            "min": 13,
            "max": 15,
            "distribution": {"medium": 5, "high": 10}
        }
    ]

    #  3. 사전 점수에 해당하는 난이도 비율 찾기
    matched = next(
        (r["distribution"] for r in difficulty_rules if r["min"] <= score <= r["max"]),
        None
    )
    if not matched:
        raise HTTPException(500, "No matching difficulty rule found")

    #  4. 전체 사후 평가 문제 불러오기
    all_questions = await db.evaluation_questions.find({"subject": subject}).to_list(length=1000)

    selected = []
    for level, count in matched.items():
        pool = [q for q in all_questions if q.get("difficulty") == level]
        if len(pool) < count:
            raise HTTPException(500, f"Not enough '{level}' level questions")
        selected += random.sample(pool, count)

    #  5. 직렬화 및 셔플
    random.shuffle(selected)
    for idx, q in enumerate(selected, 1):
        q.pop("_id", None)
        q["question_id"] = idx

    #  6. 로그 저장
    await db.posttest_logs.insert_one({
        "user_id": user_id,
        "subject": subject,
        "score": score,
        "difficulty_distribution": matched,
        "selected_ids": [q["question_id"] for q in selected],
        "timestamp": datetime.now().isoformat()
    })

    return [PreQuestion(**q) for q in selected]



# 사후 평가 제출 API
class PosttestSubmitInput(BaseModel):
    user_id: str
    subject: str
    answers: List[AnswerItem]


@router.post("/submit-posttest")
async def submit_posttest(data: PosttestSubmitInput):
    score = calculate_pretest_score(data.answers)

    await db.posttest_results.update_one(
        {"user_id": data.user_id, "subject": data.subject},
        {"$set": {
            "score": score,
            "answers": [a.dict() for a in data.answers],
            "timestamp": datetime.now().isoformat()
        }},
        upsert=True
    )

    return {"user_id": data.user_id, "subject": data.subject, "score": score}
