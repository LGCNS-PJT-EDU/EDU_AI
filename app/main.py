# main.py 또는 별도 라우터에서 사용
from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


from app.gpt_prompt import build_growth_feedback_prompt
from app.mongo_feedback import save_feedback_cache
import openai
import os
from dotenv import load_dotenv
from datetime import date
from typing import List

from app.mongodb import db

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


app = FastAPI()

class FeedbackInput(BaseModel):
    user_id: str
    pre_text: str
    post_text: str

class ScoreItem(BaseModel):
    category: str
    value:    int

class StrengthWeaknessItem(BaseModel):
    id:          str
    description: str

class Content(BaseModel):
    scores:     List[ScoreItem]
    strengths:  List[StrengthWeaknessItem]
    weaknesses: List[StrengthWeaknessItem]

    model_config = {
        "populate_by_name":  True,
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
    info:    Info
    content: Content

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

    responses = []
    for doc in docs:
        info = doc.get("info", {})
        content = doc.get("content", {})

        responses.append(
            FeedbackResponse(
                info=Info(
                    user_id=info.get("userId"),
                    date=info.get("date"),
                    subject=info.get("subject")
                ),
                content=Content(
                    scores=[ScoreItem(**s) for s in content.get("scores", [])],
                    strengths=[StrengthWeaknessItem(**s) for s in content.get("strengths", [])],
                    weaknesses=[StrengthWeaknessItem(**w) for w in content.get("weaknesses", [])]
                )
            )
        )

    serialized = [r.model_dump(by_alias=True) for r in responses]
    return JSONResponse(status_code=200, content=jsonable_encoder(serialized))