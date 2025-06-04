from datetime import date
from fastapi import HTTPException
from app.clients import db_clients
from app.utils.build_feedback_prompt import (
    build_initial_feedback_prompt_1,
    build_pre_post_comparison_prompt,
    build_post_post_comparison_prompt
)
from app.models.feedback.request import FeedbackRequest
from pydantic import ValidationError


feedback_db = db_clients["feedback"]
assessment_db = db_clients["assessment"]

# 전체 프롬프트 구성
def build_full_prompt(base_prompt: str, subject: str, user_id: str) -> str:
    today = date.today().isoformat()

    return f"""
[RAG 기반 유사 학습 정보]

[사용자 피드백 요청]
{base_prompt}

다음 조건에 맞춰 JSON 피드백을 생성하세요.


<출력 조건>
1. 모든 피드백 문장은 **존댓말**로 작성하고, 반드시 **'-습니다'** 형태의 종결어미를 사용하세요.
2. **모든 내용을 한국어로만 출력**하며, 영어 표현이나 혼용 표현은 절대 사용하지 마세요.
3. 문장은 **친절한 조언 형태**로 표현하고, **무조건적인 평가나 딱딱한 표현**은 지양하세요.
4. **챕터별 피드백은 서로 다른 표현**을 사용하여, 반복되는 문장을 피하세요.
5. **점수가 높은 챕터**는 칭찬 중심으로, **점수가 낮은 챕터**는 구체적인 개선 방향을 1~2문장으로 제시하세요.
6. 최종 코멘트(`final`)는 학습 방향에 대한 **간단한 요약 조언** 과 **전후의 전체적인 총괄적인 피드백** 을 1~2문장으로 구성하세요.
7. **유효한 JSON 형태만 반환**하세요. 마크다운, 인삿말, 코드블록(```) 등은 절대 포함하지 마세요.
8.모든 피드백 문장은 존댓말로 작성하고, 반드시 '-습니다' 형태의 종결어미를 사용하세요. 
9. 모든 내용은 한국어로 작성하며, 영어 표현이나 혼용 표현은 절대 사용하지 마세요. 
10. 피드백은 학습자에게 친절하게 조언하는 어조로 작성하며, 과도하게 단조롭거나 기계적인 표현은 피해주세요. 
11. 아래 JSON 스키마에 따라 순수 JSON 객체 **하나만** 반환하세요. 
12. 인삿말, 설명, 마크다운, 코드블록(```) 등은 절대 포함하지 마세요. 
13. JSON 구조는 유효한 형태여야 하며, 문법 오류(따옴표, 쉼표 등)가 없도록 하세요.

<추론 흐름>
- 먼저 점수(`scores`)를 확인한 뒤, 점수가 높은 챕터부터 강점을 간결하게 정리하세요.
- 이어서 점수가 낮은 챕터를 찾아 개선 방향을 제시하세요.
- 마지막으로, 전체 학습 상황을 요약한 한 문장 이상의 `final` 코멘트를 작성하세요.


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
            pre_feedback = await feedback_db.find_one(
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
            prev_feedback = await feedback_db.find_one(
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



async def generate_feedback_prompt_rev(user_id, subject, subject_id, feedback_type, nth) -> str:
    try:
        if feedback_type == "PRE":
            pre_assessment_result = await assessment_db.pre_result.find_one({ "userId": user_id, "subject.subjectId": subject_id })
            base_prompt = build_initial_feedback_prompt_1(pre_assessment_result)

        elif feedback_type == "POST" and nth == 1:
            pre_feedback = await feedback_db.find_one({ "info.userId": user_id, "info.subject": subject }, sort=[("_id", -1)])
            pre_assessment_result = await assessment_db.pre_result.find_one({ "userId": user_id, "subject.subjectId": subject_id })
            post_assessment_result = await assessment_db.post_result.find_one({ "userId": user_id, "subject.subjectId": subject_id })

            base_prompt = build_pre_post_comparison_prompt(pre_feedback, pre_assessment_result, post_assessment_result)

        else:
            post_assessments = await assessment_db.post_result.find({ "userId": user_id, "subject.subjectId": subject_id }).sort([("_id", -1)]).limit(2).to_list(length=2)

            prev_feedback = await feedback_db.find_one({ "info.userId": user_id, "info.subject": subject },sort=[("_id", -1)])
            post_assessment_e = post_assessments[1]
            post_assessment_z = post_assessments[0]

            base_prompt = build_post_post_comparison_prompt(prev_feedback, post_assessment_e, post_assessment_z)

        return base_prompt

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 프롬프트 생성 오류: {str(e)}")