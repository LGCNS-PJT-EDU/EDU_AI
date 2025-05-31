from datetime import date

from fastapi import HTTPException

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


async def build_full_prompt(prompt, subject, user_id):
    try:
        #           base_prompt = build_feedback_prompt(data)
        base_prompt = prompt

        # RAG 검색 통합
        #        context_docs = retrieve_similar_docs(data.post_text or data.pre_text or "")
        #        context_text = "\n".join(context_docs)

        full_prompt = f"""
        [RAG 기반 유사 학습 정보]

        [사용자 피드백 요청]
        {base_prompt}

        아래 **JSON 스키마**에 맞춰서 **순수 JSON 객체** 하나만 반환해주세요.  
        다른 설명, 마크다운, 코드 블록(```…)은 절대 포함하지 마세요.

        {{
          "info": {{
            "userId": "{user_id}",
            "date": "{date.today().isoformat()}",
            "subject": "{subject}"
          }},
          "scores": {{
            /* 챕터별 점수와 total 포함 */
            "chapter1": 0,
            "chapter2": 0,
            // …,
            "total": 0
          }},
          "feedback": {{
            "strength": {{
              /* 챕터별 강점 코멘트 */
              "chapter1": "",
              // …
            }},
            "weakness": {{
              /* 챕터별 약점 코멘트 */
              "chapter2": "",
              // …
            }},
            "final": ""  /* 최종 요약 코멘트 */
          }}
        }}
        """


    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return full_prompt