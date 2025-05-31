from datetime import date
from fastapi import HTTPException
<<<<<<< HEAD
from app.clients.mongodb import db
from app.utils.build_feedback_prompt import (
    build_initial_feedback_prompt_1,
    build_pre_post_comparison_prompt,
    build_post_post_comparison_prompt
)
from app.models.feedback.request import FeedbackRequest
from pydantic import ValidationError


# 전체 프롬프트 구성
def build_full_prompt(base_prompt: str, subject: str, user_id: str) -> str:
    today = date.today().isoformat()

    return f"""
[RAG 기반 유사 학습 정보]

[사용자 피드백 요청]
{base_prompt}

모든 피드백 문장은 **존댓말**로 작성하고, 반드시 **'-습니다'** 형태의 종결어미를 사용하세요.  
또한, **모든 내용을 한국어로 출력**하고 영어 또는 혼용 표현을 사용하지 마세요.

아래 **JSON 스키마**에 맞춰서 **순수 JSON 객체** 하나만 반환해주세요.  
다른 설명, 마크다운, 코드 블록(```…)은 절대 포함하지 마세요.
=======

from app.clients import db_clients
from app.utils.build_feedback_prompt import build_initial_feedback_prompt, build_pre_post_comparison_prompt, build_post_post_comparison_prompt


feedback_db = db_clients["feedback"]

async def set_prompt(data, post_assessments, subject, user_id):
    if not post_assessments:
        pre_assessment = data.get("pre_assessment", {}).get("subject", {})
        prompt = build_initial_feedback_prompt(pre_assessment)
    elif len(post_assessments) == 1:
        pre_feedback = await feedback_db.feedback.find_one({"info.userId": user_id, "info.subject": subject}, sort=[("_id", 1)])
        pre_assessment = data.get("pre_assessment", {}).get("subject", {})
        prompt = build_pre_post_comparison_prompt(pre_feedback, pre_assessment, post_assessments[-1][1])
    else:
        prev_feedback = await feedback_db.feedback.find_one({"info.userId": user_id, "info.subject": subject}, sort=[("_id", -1)])
        prompt = build_post_post_comparison_prompt(prev_feedback, post_assessments[-2][1], post_assessments[-1][1])
    return prompt
>>>>>>> 457b174 (EDU-497 feat: DB 클라이언트와 여기에 기반한 DB 객체를 추가)


{{
  "info": {{
    "userId": "{user_id}",
    "date": "{today}",
    "subject": "{subject}"
  }},
  "scores": {{
    "chapter1": 0,
    "chapter2": 0,
    "chapter3": 0,
    "chapter4": 0,
    "chapter5": 0,
    "total": 0
  }},
  "feedback": {{
    "strength": {{
      "chapter1": ""
    }},
    "weakness": {{
      "chapter2": ""
    }},
    "final": ""
  }}
}}
""".strip()


# 상황별 프롬프트 생성
async def generate_feedback_prompt(data, post_assessments, subject: str, user_id: str) -> str:
    try:
        if not post_assessments:
            try:
                subject_data = data.get("pre_assessment", {}).get("subject", {})
                questions = data.get("pre_assessment", {}).get("questions", [])

                pre_score = sum(1 for q in questions if q.get("answerTF") is True)

                pre_assessment = FeedbackRequest(
                    user_id=user_id,
                    subject=subject,
                    chapter="전체",  # 단원 정보가 없거나 통합일 경우
                    pre_score=pre_score
                )

                base_prompt = build_initial_feedback_prompt_1(pre_assessment)

            except ValidationError as ve:
                raise HTTPException(status_code=422, detail=f"입력 데이터 오류: {str(ve)}")

        elif len(post_assessments) == 1:
            pre_feedback = await db.feedback.find_one(
                {"info.userId": user_id, "info.subject": subject},
                sort=[("_id", 1)]
            )
            pre_assessment = data.get("pre_assessment", {}).get("subject", {})
            base_prompt = build_pre_post_comparison_prompt(
                pre_feedback,
                pre_assessment,
                post_assessments[-1][1]
            )

        else:
            prev_feedback = await db.feedback.find_one(
                {"info.userId": user_id, "info.subject": subject},
                sort=[("_id", -1)]
            )
            base_prompt = build_post_post_comparison_prompt(
                prev_feedback,
                post_assessments[-2][1],
                post_assessments[-1][1]
            )

        return build_full_prompt(base_prompt, subject, user_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 프롬프트 생성 오류: {str(e)}")