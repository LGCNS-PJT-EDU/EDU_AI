from fastapi import APIRouter
from pydantic import BaseModel
from app.gpt_prompt import build_growth_feedback_prompt
from app.mongo_feedback import save_feedback_cache
import openai

router = APIRouter()

class FeedbackInput(BaseModel):
    user_id: str
    pre_text: str
    post_text: str

@router.post("/generate-feedback")
async def generate_feedback(data: FeedbackInput):
    prompt = build_growth_feedback_prompt(data.pre_text, data.post_text)

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
