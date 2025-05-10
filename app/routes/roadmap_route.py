from fastapi import APIRouter
from pydantic import BaseModel
from app.mongodb import db
from app.mongo_roadmap import save_roadmap_cache
from app.gpt_prompt import build_roadmap_prompt
from app.roadmap_rag import generate_roadmap_rag

router = APIRouter()

class RoadmapRequest(BaseModel):
    user_id: str

@router.post("/generate-roadmap")
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

    return {"roadmap": roadmap}
