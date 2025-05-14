from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.mongodb import db
from datetime import datetime
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

@router.get("/get-pretest")
async def get_pretest(user_id: str):
    # 1. 사용자 정보 조회
    user = await db.user_profiles.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    track = user.get("track", "frontend")
    level = user.get("calculated_level", 0)

    # 2. 해당 트랙/레벨 문제 로딩
    all_questions = await db.evaluation_questions.find({
        "track": track,
        "level": level
    }).to_list(length=1000)

    # 3. 챕터별 그룹핑
    grouped = {}
    for q in all_questions:
        chapter = q['question_id'].split('_')[0]
        grouped.setdefault(chapter, []).append(q)

    # 4. 챕터별 low/medium 하나씩 뽑기
    selected = []
    for qlist in grouped.values():
        lows = [q for q in qlist if q['difficulty'] == "low"]
        meds = [q for q in qlist if q['difficulty'] == "medium"]
        if lows:
            selected.append(random.choice(lows))
        if meds:
            selected.append(random.choice(meds))
        if len(selected) >= 10:
            break

    # 5. 직렬화 오류 방지 (_id 제거)
    for q in selected:
        q.pop('_id', None)

    # 6. MongoDB에 문제 이력 저장
    await db.pretest_logs.insert_one(build_pretest_log(user_id, selected))

    # 7. 클라이언트에 반환
    return {
        "questions": selected[:10],
        "metadata": {
            "user_id": user_id,
            "track": track,
            "level": level,
            "question_ids": [q["question_id"] for q in selected],
            "timestamp": datetime.now().isoformat()
        }
    }