import json
from datetime import date

import openai
from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.clients.mongodb import db
from app.models.feedback.request import FeedbackRequest
from app.models.feedback.response import FeedbackResponse, Info, Feedback
from typing import List

from app.services.rag_module import retrieve_similar_docs
from app.utils.build_feedback_prompt import build_feedback_prompt

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


@router.post("/generate-feedback", response_model=List[FeedbackResponse], response_model_by_alias=True, summary="지정한 사용자의 피드백을 생성", description="해당 유저의 직전 테스트 결과와 이번 테스트 결과를 활용해서 피드백을 생성한다.")
async def generate_feedback(data: FeedbackRequest, userId: str):
    data.user_id = userId

    try:
        base_prompt = build_feedback_prompt(data)

        # RAG 검색 통합
        context_docs = retrieve_similar_docs(data.post_text or data.pre_text or "")
        context_text = "\n".join(context_docs)

        # 프롬프트 최종 구성
        full_prompt = f"""
[RAG 기반 유사 학습 정보]
{context_text}

[사용자 피드백 요청]
{base_prompt}
"""
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    #  GPT 호출
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 학습 성장 분석가입니다."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    feedback_text = response.choices[0].message.content

    # JSON parse
    try:
        parsed = json.loads(feedback_text)
        info = parsed["info"]
        scores = parsed["scores"]
        feedback = parsed["feedback"]
    except json.JSONDecodeError:
        info = {
            "userId": data.user_id,
            "date": date.today().isoformat(),
            "subject": data.subject
        }
        scores = {
            **data.scores,
        }
        scores["total"] = sum(scores.values())
        feedback = {
            "strength": {},
            "weakness": {},
            "final": feedback_text
        }

    #  MongoDB 저장
    await db.feedback.insert_one({
        "user_id": data.user_id,
        "info": info,
        "scores": scores,
        "feedback": {
            "strength": feedback.get("strength", {}),
            "weakness": feedback.get("weakness", {}),
            "final": feedback.get("final", "")
        }
    })

    return_json = {
        "info": info,
        "scores": scores,
        "feedback": feedback
    }

    return JSONResponse(status_code=200, content=jsonable_encoder([return_json]))