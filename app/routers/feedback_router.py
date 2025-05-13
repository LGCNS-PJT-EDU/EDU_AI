import openai
from datetime import date
from typing import List

from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.clients.mongodb import db
from app.models.feedback.request import FeedbackRequest
from app.models.feedback.response import FeedbackResponse, Info, Feedback
from app.utils.gpt_prompt import (
    build_initial_feedback_prompt,
    build_pre_post_comparison_prompt,
    build_post_post_comparison_prompt
)

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
    return JSONResponse(status_code=200, content=jsonable_encoder(serialized))


@router.post("/generate-feedback", summary="사용자의 피드백을 생성", description="ChatGPT를 활용해서 해당 사용자의 피드백을 생성한다.")
async def generate_feedback(data: FeedbackRequest):
    chapter = data.chapter
    user_id = data.user_id

    # 사전 평가 여부 확인
    pre_doc = await db.feedback.find_one({
        "info.userId": user_id,
        "info.chapter": chapter,
        "info.type": "pre"
    })

    # 현재 사후 평가 횟수 확인
    post_docs = await db.feedback.find({
        "info.userId": user_id,
        "info.chapter": chapter,
        "info.type": "post"
    }).sort("info.date", -1).to_list(length=2)

    # 피드백 프롬프트 생성
    if not pre_doc:
        # 사전 평가 최초
        prompt = build_initial_feedback_prompt(data)
        feedback_type = "pre"
    elif not post_docs:
        # 첫 사후 평가
        prompt = build_pre_post_comparison_prompt(pre_doc, data)
        feedback_type = "post"
    else:
        # 이전 사후와 비교
        previous_post = post_docs[0]
        prompt = build_post_post_comparison_prompt(previous_post, data)
        feedback_type = "post"

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

    # DB 저장
    await db.feedback.insert_one({
        "user_id": user_id,
        "info": {
            "userId": user_id,
            "date": date.today().isoformat(),
            "subject": data.subject,
            "chapter": chapter,
            "type": feedback_type
        },
        "scores": {
            "pre": data.pre_score,
            "post": data.post_score
        },
        "feedback": {
            "text": feedback_text
        }
    })

    return {
        "user_id": user_id,
        "chapter": chapter,
        "feedback_type": feedback_type,
        "feedback": feedback_text
    }
