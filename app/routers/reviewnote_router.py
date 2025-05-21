# 📁 app/routers/reviewnote_router.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
import openai
import os
import json
import re
from datetime import datetime

from app.clients.mongodb import db

router = APIRouter()

#  1. 입력 데이터 스키마 정의
class QuestionItem(BaseModel):
    question_id: str
    question: str
    options: List[str]
    correct_answer: str
    user_answer: str

class ReviewNoteRequest(BaseModel):
    user_id: str
    subject: str
    phase: str  # "pre" or "post"
    questions: List[QuestionItem]

#  2. GPT 프롬프트 구성 함수
def build_reviewnote_prompt(question, options, correct_answer, user_answer):
    return f"""
당신은 교육 전문가 AI입니다.

다음은 사용자가 틀린 문제입니다:

질문: {question}
보기: {options}
사용자 답변: {user_answer}
정답: {correct_answer}

1. 사용자가 왜 틀렸는지 설명해주세요.
2. 해당 개념을 간단히 설명해주세요.
3. 추천 학습 키워드 3개를 제시해주세요.

※ 반드시 JSON 형식으로 출력해주세요:
{{
  "wrong_reason": "...",
  "concept_summary": "...",
  "recommend_keywords": ["...", "...", "..."]
}}
"""

#  3. GPT 호출 함수
def call_gpt(prompt: str) -> dict:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 교육 전문가 AI입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=700
        )
        content = response.choices[0].message.content.strip()
        content = re.sub(r"^```json|```$", "", content)
        return json.loads(content)
    except Exception as e:
        print("GPT 오류:", e)
        return {
            "wrong_reason": "GPT 응답 실패",
            "concept_summary": "",
            "recommend_keywords": []
        }

#  4. 메인 API 라우터
@router.post("/generate", summary="사전/사후 오답노트 자동 생성")
async def generate_reviewnote(request: ReviewNoteRequest):
    results = []

    for q in request.questions:
        if q.user_answer != q.correct_answer:
            prompt = build_reviewnote_prompt(
                q.question, q.options, q.correct_answer, q.user_answer
            )
            gpt_result = call_gpt(prompt)

            result_doc = {
                "user_id": request.user_id,
                "subject": request.subject,
                "phase": request.phase,  # "pre" or "post"
                "question_id": q.question_id,
                "question": q.question,
                "user_answer": q.user_answer,
                "correct_answer": q.correct_answer,
                "created_at": datetime.utcnow(),
                "review_note": gpt_result
            }
            await db["reviewnote"].insert_one(result_doc)
            results.append(result_doc)

    return {"created": len(results), "reviewnotes": results}
