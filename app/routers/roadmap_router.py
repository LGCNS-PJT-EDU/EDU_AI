# app/routers/roadmap_router.py
from fastapi import APIRouter, Query
from pydantic import BaseModel
from app.utils.gpt_prompt import (
    call_gpt,
    build_roadmap_prompt,
    build_strategy_prompt
)
from app.services.mongo_recommendation import get_recommended_contents_by_subject
from app.clients.mongodb import save_explanation_log
from app.services.roadmap_vectorstore import save_explanation_to_chroma


router = APIRouter()

# ------------------------------
# 로드맵 설명 API
# ------------------------------
class ExplainRequest(BaseModel):
    user_id: str
    track: str
    level: str
    goal: str
    subjects: list[str]

@router.post("/explain-roadmap", tags=["로드맵 설명"])
async def explain_roadmap(data: ExplainRequest):
    user_profile = {
        "track": data.track,
        "level": data.level,
        "goal": data.goal
    }

    prompt = build_roadmap_prompt(user_profile)
    subject_list = ", ".join(data.subjects)
    prompt += f"\n\n현재 추천된 학습 유닛은 다음과 같습니다:\n{subject_list}\n\n각 유닛이 포함된 이유도 함께 설명해주세요."

    explanation = await call_gpt(prompt)

    # MongoDB 저장
    await save_explanation_log({
        "user_id": data.user_id,
        "track": data.track,
        "level": data.level,
        "goal": data.goal,
        "subjects": data.subjects,
        "gpt_prompt": prompt,
        "gpt_response": explanation
    })

    # ChromaDB 저장
    save_explanation_to_chroma(
        user_id=data.user_id,
        explanation=explanation,
        metadata={
            "track": data.track,
            "level": data.level,
            "goal": data.goal,
            "subjects": data.subjects
        }
    )

    return {
        "user_id": data.user_id,
        "explanation": explanation
    }




# ------------------------------
# 학습 전략 추천 API
# ------------------------------
class StrategyRequest(BaseModel):
    user_id: str
    subjects: list[str]
    level: str
    style: str  # 예: 실습 중심, 영상 중심, 공식문서 선호 등
    available_time: str  # 예: 주 5시간, 하루 1시간 등

@router.post("/generate-strategy", tags=["학습 전략 추천"])
async def generate_strategy(data: StrategyRequest):
    prompt = build_strategy_prompt(
        subjects=data.subjects,
        level=data.level,
        style=data.style,
        available_time=data.available_time
    )

    strategy = await call_gpt(prompt)
    return {
        "user_id": data.user_id,
        "strategy": strategy
    }

# ------------------------------
# 콘텐츠 추천 API
# ------------------------------
@router.get("/recommend-contents", tags=["콘텐츠 추천"])
async def recommend_contents(subject_name: str = Query(...)):
    results = await get_recommended_contents_by_subject(subject_name)
    return {"subject_name": subject_name, "contents": results}
