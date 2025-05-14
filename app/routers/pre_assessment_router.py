from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.mongodb import db
from datetime import datetime

from app.models.pre_assessment.response import PreQuestion
from app.utils.pretest_log_utils import build_pretest_log
from app.utils.level_utils import calculate_level_from_answers
from typing import List
import random

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

# pre-test 결과 저장
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



#  1. 사용자 설문 + 진단 저장
class AssessmentInput(BaseModel):
    user_id: str
    survey_answers: dict
    pre_test_score: int


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

# 사전 평가 문제 반환
@router.get("/subject", response_model=List[PreQuestion])
async def get_pretest(user_id:str, subject_id: int):
    # 1. 사용자 정보 조회
    user = await db.user_profiles.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    e_level = user.get("level")
    print(e_level)

    # 2) techMap 문서 한 번 불러오기
    mapping = await db.techMap.find_one({})
    if not mapping:
        raise HTTPException(status_code=500, detail="Tech map not initialized")

    # 3) subject_name (숫자 키) 조회
    subject_name = mapping.get(str(subject_id))
    if not subject_name:
        raise HTTPException(status_code=404, detail="Subject not found")
    print(subject_name)

    # 4) Korean level (영어 키) 조회
    difficulties_doc = await db.techMap.find_one({"difficulties": {"$exists": True}})
    if not difficulties_doc:
        raise HTTPException(500, "Difficulties mapping not found")

    k_level = difficulties_doc["difficulties"].get(e_level)

    print(k_level)

    question_count = {}
    if k_level == "하":
        question_count["상"], question_count["중"], question_count["하"] = 2, 5, 8
    elif k_level == "중":
        question_count["상"], question_count["중"], question_count["하"] = 4, 6, 5
    elif k_level == "상":
        question_count["상"], question_count["중"], question_count["하"] = 7, 5, 3
    else:
        raise HTTPException(status_code=500, detail="Forbidden attempt occurred")


    # 2. 해당 트랙/레벨 문제 로딩
    all_questions = await db[subject_name].find().to_list(length=1000)

    hard_qs = [q for q in all_questions if q["difficulty"] == "상"]
    mid_qs = [q for q in all_questions if q["difficulty"] == "중"]
    easy_qs = [q for q in all_questions if q["difficulty"] == "하"]

    def safe_sample(pool, cnt):
        if len(pool) < cnt:
            raise HTTPException(
                status_code=500,
                detail=f"Not enough questions: required {cnt}, got {len(pool)}"
            )
        return random.sample(pool, cnt)

    selected = []
    selected += safe_sample(hard_qs, question_count["상"])
    selected += safe_sample(mid_qs,  question_count["중"])
    selected += safe_sample(easy_qs, question_count["하"])

    # 4) 최종 섞기
    random.shuffle(selected)

    # 5) question_id 부여 및 모델 변환
    results: List[PreQuestion] = []
    for idx, doc in enumerate(selected, start=1):
        doc.pop("_id", None)
        doc["question_id"] = idx
        results.append(PreQuestion(**doc))


    return results