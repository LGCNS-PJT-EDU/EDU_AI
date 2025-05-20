# app/routers/roadmap_router.py

from fastapi import APIRouter, Query
from pydantic import BaseModel

from app.clients.mongodb import db, save_explanation_log
from app.services.mongo_roadmap import save_roadmap_cache
from app.services.mongo_recommendation import get_recommended_contents_by_subject
from app.services.roadmap_rag import generate_roadmap_rag
from app.services.roadmap_vectorstore import save_explanations_to_chroma
from app.utils.gpt_prompt import (
    call_gpt,
    build_roadmap_prompt,
    build_strategy_prompt
)

router = APIRouter()

# ------------------------------
#  Pydantic 모델
# ------------------------------
class RoadmapRequest(BaseModel):
    user_id: str

class ExplainRequest(BaseModel):
    user_id: str
    track: str
    level: str
    goal: str
    subjects: list[str]

class StrategyRequest(BaseModel):
    user_id: str
    subjects: list[str]
    level: str
    style: str
    available_time: str

# ------------------------------
#  GPT 로드맵 생성 API
# ------------------------------
@router.post("/generate-roadmap", tags=["로드맵 생성"])
async def generate_roadmap(data: RoadmapRequest):
    user_profile = await db.user_profiles.find_one({"user_id": data.user_id})
    if not user_profile:
        return {"error": "user not found"}

    prompt = build_roadmap_prompt(user_profile)
    roadmap_text = generate_roadmap_rag(prompt)

    roadmap = [{
        "title": "GPT 추천 로드맵",
        "description": roadmap_text,
        "reason": "Chroma + GPT 기반"
    }]
    await save_roadmap_cache(data.user_id, roadmap)

    return {"user_id": data.user_id, "roadmap": roadmap}

# ------------------------------
#  GPT 로드맵 설명 API
# ------------------------------
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

    await save_explanation_log({
        "user_id": data.user_id,
        **user_profile,
        "subjects": data.subjects,
        "gpt_prompt": prompt,
        "gpt_response": explanation
    })

    save_explanations_to_chroma(
        user_id=data.user_id,
        explanations=explanation,
        metadata=user_profile | {"subjects": data.subjects}
    )

    return {"user_id": data.user_id, "explanation": explanation}

# ------------------------------
#  GPT 학습 전략 추천 API
# ------------------------------
@router.post("/generate-strategy", tags=["학습 전략 추천"])
async def generate_strategy(data: StrategyRequest):
    prompt = build_strategy_prompt(
        subjects=data.subjects,
        level=data.level,
        style=data.style,
        available_time=data.available_time
    )

    strategy = await call_gpt(prompt)

    roadmap = [{
        "title": "GPT 추천 로드맵",
        "description": strategy,
        "reason": "Chroma + GPT 기반"
    }]
    await save_roadmap_cache(data.user_id, roadmap)

    return {
        "user_id": data.user_id,
        "strategy": strategy,
        "roadmap": roadmap
    }

# ------------------------------
#  콘텐츠 추천 API
# ------------------------------
@router.get("/recommend-contents", tags=["콘텐츠 추천"])
async def recommend_contents(subject_name: str = Query(...)):
    results = await get_recommended_contents_by_subject(subject_name)
    return {"subject_name": subject_name, "contents": results}

