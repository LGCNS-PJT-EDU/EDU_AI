# main.py 또는 별도 라우터에서 사용
from fastapi import FastAPI
from pydantic import BaseModel
from app.gpt_prompt import build_growth_feedback_prompt
from app.mongo_feedback import save_feedback_cache
import openai
import os
from dotenv import load_dotenv

from app.mongodb import db

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


app = FastAPI()

class FeedbackInput(BaseModel):
    user_id: str
    pre_text: str
    post_text: str

class FeedbackResponse(BaseModel):
    user_id: str
    text: str


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

@app.get("/feedback/{user_id}", response_model=FeedbackResponse)
async def return_feedback(user_id: str):
    col = db["feedback"]

    doc = await col.find_one({"user_id": user_id})

    return FeedbackResponse(user_id=user_id, text=doc.get("text"))
