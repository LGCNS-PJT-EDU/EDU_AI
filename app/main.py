# app/main.py
from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from app.gpt_prompt import build_growth_feedback_prompt
from app.mongo_feedback import save_feedback_cache
import openai
import os
from datetime import date
from typing import List, Dict
from app.mongodb import db


#  라우터들 먼저 import
from app.routes.assessment import router as assessment_router
from app.routes.post_assessment import router as post_assessment_router
from app.routes.activity_log import router as activity_log_router
from app.routes.roadmap_route import router as roadmap_router
from app.routes.feedback_route import router as feedback_router

#  환경 변수 및 OpenAI 키 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#  FastAPI 인스턴스 정의
app = FastAPI(
    title="AI 학습 플랫폼 API",
    version="1.0.0",
    description="진단 기반 개인 맞춤형 로드맵 및 성장 피드백 생성 API"
)

#  라우터 등록 (순서 중요)
app.include_router(assessment_router, prefix="/api/v1")
app.include_router(post_assessment_router, prefix="/api/v1")
app.include_router(activity_log_router, prefix="/api/v1")
app.include_router(roadmap_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")


class FeedbackInput(BaseModel):
    user_id: str
    pre_text: str
    post_text: str

class Feedback(BaseModel):
    strength: Dict[str, str]
    weakness: Dict[str, str]
    final: str

    model_config = {
        "populate_by_name": True,
        "populate_by_alias": True
    }

class Info(BaseModel):
    user_id: str  = Field(..., alias="userId")
    date:    date
    subject: str

    model_config = {
        "populate_by_name":  True,
        "populate_by_alias": True
    }

class FeedbackResponse(BaseModel):
    info: Info
    scores: Dict[str, int]
    feedback: Feedback

    model_config = {
        "populate_by_name":  True,
        "populate_by_alias": True
    }


@app.post("/generate-feedback")
async def generate_feedback(data: FeedbackInput):
    prompt = build_growth_feedback_prompt(data.pre_text, data.post_text)

    # GPT 호출
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 학습 성장 분석가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

    feedback_text = response['choices'][0]['message']['content']
    await save_feedback_cache(data.user_id, feedback_text)

    return {"feedback": feedback_text}

@app.get("/feedback", response_model=List[FeedbackResponse], response_model_by_alias=True)
async def list_feedbacks(userId: str):
    target = db["feedback"].find({"info.userId": userId})
    docs = await target.to_list(length=1000)

    responses: List[FeedbackResponse] = []
    for doc in docs:
        info_dict = doc.get("info", {})
        scores_dict = doc.get("scores", {})
        feedback_dict = doc.get("feedback", {})

        responses.append(
            FeedbackResponse(
                info=Info(**info_dict),
                scores=scores_dict,
                feedback=Feedback(**feedback_dict)
            )
        )

    serialized = [r.model_dump(by_alias=True) for r in responses]
    return JSONResponse(status_code=200, content=jsonable_encoder(serialized))