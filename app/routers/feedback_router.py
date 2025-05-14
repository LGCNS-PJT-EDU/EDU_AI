import json
import re
from datetime import date

import openai


from fastapi import APIRouter, HTTPException
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
    return JSONResponse(status_code=200, content=jsonable_encoder(serialized))


@router.post("/generate-feedback", response_model=List[FeedbackResponse], response_model_by_alias=True, summary="지정한 사용자의 피드백을 생성", description="해당 유저의 직전 테스트 결과와 이번 테스트 결과를 활용해서 피드백을 생성한다.")
async def generate_feedback(data: FeedbackRequest, userId: str, subject: str):
    data.user_id = userId
    data.subject = subject

    pre_count = await db.feedback.count_documents(
        {"info.userId": data.user_id, "info.subject": data.subject, "info.type": "pre"}
    )

    post_count = await db.feedback.count_documents(
        {"info.userId": data.user_id, "info.subject": data.subject, "info.type": "post"}
    )


    # 피드백 프롬프트 생성
    if pre_count == 0:
        # 사전 평가 최초
        prompt = build_initial_feedback_prompt(data)
        feedback_type = "pre"
    elif post_count == 0:
        # 첫 사후 평가
        pre_doc = await db.feedback.find_one({"info.userId": data.user_id, "info.subject": data.subject}, sort=[("_id", 1)])
        prompt = build_pre_post_comparison_prompt(pre_doc, data)
        feedback_type = "post"
    else:
        # 이전 사후와 비교
        previous_post = await db.feedback.find_one({"info.userId": data.user_id, "info.subject": data.subject}, sort=[("_id", -1)])
        prompt = build_post_post_comparison_prompt(previous_post, data)
        feedback_type = "post"

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
※ 반드시 순수 JSON 객체 하나만 반환해주세요. 다른 설명이나 코드블록은 모두 제거해주세요. ※
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
        text_reg = feedback_text.strip()
        text_reg = re.sub(r"^```json\s*|\s*```$", "", text_reg)
        match = re.search(r"\{.*\}", text_reg, re.DOTALL)
        if match:
            text_reg = match.group(0)

        print(text_reg)


        parsed = json.loads(text_reg)
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
