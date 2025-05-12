import openai
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder

from app.clients.mongodb import db
from app.models.feedback.request import FeedbackRequest
from app.models.feedback.response import FeedbackResponse, Info, Feedback
from typing import List

from app.services.mongo_feedback import save_feedback_cache
from app.utils.gpt_prompt import build_growth_feedback_prompt

router = APIRouter()

@router.get("", response_model=List[FeedbackResponse], response_model_by_alias=True, summary="지정한 사용자의 피드백을 반환", description="해당 유저의 전체 피드백을 반환한다.")
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
    from starlette.responses import JSONResponse
    return JSONResponse(status_code=200, content=jsonable_encoder(serialized))


@router.post("/generate-feedback", summary="사용자의 피드백을 생성", description="ChatGPT를 활용해서 해당 사용자의 피드백을 생성한다.")
async def generate_feedback(data: FeedbackRequest):
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