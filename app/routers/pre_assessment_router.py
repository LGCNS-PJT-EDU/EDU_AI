from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.mongodb import db
from datetime import datetime
from app.models.pre_assessment.response import PreQuestion
from app.services.assessment.common import get_user, subject_id_to_name
from app.utils.level_utils import calculate_level_from_answers
from typing import List
import random
import json
import os

router = APIRouter()

# ------------------ 사전 평가 제출 및 점수 계산 ------------------

class AnswerItem(BaseModel):
    question_id: str
    correct: bool
    difficulty: str

class PretestSubmitInput(BaseModel):
    user_id: str
    answers: List[AnswerItem]

def calculate_pretest_score(answers: List[AnswerItem]) -> int:
    score = 0
    for ans in answers:
        if ans.correct:
            if ans.difficulty == "low":
                score += 1
            elif ans.difficulty == "medium":
                score += 3
    return score

@router.post("/submit-pretest")
async def submit_pretest(data: PretestSubmitInput):
    score = calculate_pretest_score(data.answers)

    await db.pretest_results.update_one(
        {"user_id": data.user_id},
        {"$set": {
            "score": score,
            "answers": [a.dict() for a in data.answers],
            "timestamp": datetime.now().isoformat()
        }},
        upsert=True
    )

    return {"user_id": data.user_id, "score": score}


# ------------------ 사용자 설문 및 진단 저장 ------------------
class AssessmentInput(BaseModel):
    user_id: str
    survey_answers: dict
    pre_test_score: int

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


# ------------------ 사전 평가 문제 출제 ------------------
@router.get("/get-pretest", response_model=List[PreQuestion], response_model_by_alias=False)
async def get_pretest(user_id: str, subject_id: int):
    user = await get_user(user_id)
    level = user.get("level")

    if level is not None:
        raise HTTPException(status_code=404, detail="Pre-test already done")

    subject_name = await subject_id_to_name(subject_id)

    all_questions = await db.evaluation_questions.find({"subject": subject_name}).to_list(length=1000)
    chapter_names = {q["chapterName"] for q in all_questions}

    selected = []
    for chapter in chapter_names:
        mid_qs = [q for q in all_questions if q["chapterName"] == chapter and q["difficulty"] == "medium"]
        easy_qs = [q for q in all_questions if q["chapterName"] == chapter and q["difficulty"] == "low"]

        selected += random.sample(mid_qs, min(len(mid_qs), 1))
        selected += random.sample(easy_qs, min(len(easy_qs), 1))

    random.shuffle(selected)
    results = []
    for idx, doc in enumerate(selected, start=1):
        doc.pop("_id", None)
        doc["question_id"] = idx
        results.append(PreQuestion(**doc))

    await db.pretest_logs.insert_one({
        "user_id": user_id,
        "subject": subject_name,
        "selected_ids": [q["question_id"] for q in selected],
        "timestamp": datetime.now().isoformat()
    })

    return results


# ------------------ 난이도 분포 기반 사후 평가 문제 출제 ------------------
@router.get("/get-posttest", response_model=List[PreQuestion], response_model_by_alias=False)
async def get_posttest(user_id: str, subject_id: int):
    user = await db.user_profiles.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    e_level = user.get("level")
    mapping = await db.techMap.find_one({})
    if not mapping:
        raise HTTPException(status_code=500, detail="Tech map not initialized")

    subject_name = mapping.get(str(subject_id))
    if not subject_name:
        raise HTTPException(status_code=404, detail="Subject not found")

    with open("config/difficulty_rules.json", "r", encoding="utf-8") as f:
        DIFFICULTY_RULES = json.load(f)

    rule = DIFFICULTY_RULES.get(e_level)
    if not rule:
        raise HTTPException(status_code=500, detail="Invalid level")

    all_questions = await db.evaluation_questions.find({"subject": subject_name}).to_list(length=1000)

    def safe_sample(pool, cnt):
        if len(pool) < cnt:
            raise HTTPException(500, f"Not enough questions in pool (required {cnt}, found {len(pool)})")
        return random.sample(pool, cnt)

    selected = []
    for level, count in rule.items():
        pool = [q for q in all_questions if q["difficulty"] == level]
        selected += safe_sample(pool, count)

    random.shuffle(selected)
    results: List[PreQuestion] = []
    for idx, doc in enumerate(selected, start=1):
        doc.pop("_id", None)
        doc["question_id"] = idx
        results.append(PreQuestion(**doc))

    await db.posttest_logs.insert_one({
        "user_id": user_id,
        "subject": subject_name,
        "selected_ids": [q["question_id"] for q in selected],
        "difficulty_distribution": rule,
        "timestamp": datetime.now().isoformat()
    })

    return results
