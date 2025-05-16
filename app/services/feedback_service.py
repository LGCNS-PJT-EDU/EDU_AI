# app/services/feedback_service.py
import json, re
from datetime import date
from app.clients.mongodb import db
from app.utils.gpt_prompt import (
    build_initial_feedback_prompt,
    build_pre_post_comparison_prompt,
    build_post_post_comparison_prompt
)
from app.utils.build_feedback_prompt import build_feedback_prompt
from app.models.feedback.request import FeedbackRequest
from app.services.rag_module import retrieve_similar_docs
import openai

async def generate_feedback_by_gpt(data: FeedbackRequest):
    # 기존 피드백 개수 확인
    pre_count = await db.feedback.count_documents({"info.userId": data.user_id, "info.subject": data.subject, "info.type": "pre"})
    post_count = await db.feedback.count_documents({"info.userId": data.user_id, "info.subject": data.subject, "info.type": "post"})

    if pre_count == 0:
        prompt = build_initial_feedback_prompt(data)
    elif post_count == 0:
        pre_doc = await db.feedback.find_one({"info.userId": data.user_id, "info.subject": data.subject}, sort=[("_id", 1)])
        prompt = build_pre_post_comparison_prompt(pre_doc, data)
    else:
        prev_post = await db.feedback.find_one({"info.userId": data.user_id, "info.subject": data.subject}, sort=[("_id", -1)])
        prompt = build_post_post_comparison_prompt(prev_post, data)

    # RAG + 기본 프롬프트
    base_prompt = build_feedback_prompt(data)
    context_docs = retrieve_similar_docs(data.post_text or data.pre_text or "")
    context_text = "\n".join(context_docs)

    full_prompt = f"""
[RAG 기반 유사 학습 정보]
{context_text}

[사용자 피드백 요청]
{base_prompt}
※ 반드시 순수 JSON 객체 하나만 반환해주세요. 다른 설명이나 코드블록은 모두 제거해주세요. ※
"""

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

    # GPT 결과 처리
    try:
        text_reg = re.sub(r"^```json\s*|\s*```$", "", feedback_text.strip())
        match = re.search(r"\{.*\}", text_reg, re.DOTALL)
        if match:
            text_reg = match.group(0)
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
        scores = {**data.scores, "total": sum(data.scores.values())}
        feedback = {
            "strength": {},
            "weakness": {},
            "final": feedback_text
        }

    result = {
        "info": info,
        "scores": scores,
        "feedback": feedback
    }

    await db.feedback.insert_one(result)
    return result
