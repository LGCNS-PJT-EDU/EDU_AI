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
from app.services.common.common import subject_id_to_name
from app.utils.build_feedback_prompt import (
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


@router.post("",  summary="지정한 사용자의 피드백을 생성", description="해당 유저의 직전 테스트 결과와 이번 테스트 결과를 활용해서 피드백을 생성한다.")
async def generate_feedback(userId: str, subjectId: int):
    user_id = userId
    subject_id = subjectId
    subject = await subject_id_to_name(subject_id)
    print(user_id, subject_id, subject)

    data = await db.user_profiles.find_one({"user_id": user_id})
    if not data:
        raise HTTPException(status_code=404, detail="No User Found")
    print(data)

    has_pre = data.get("pre_assessment", {}).get("subject", {}).get("subjectId") == subject_id
    print(has_pre)

    post_count = sum(
        1
        for k, a in data.items()
        if k.startswith("post_assessment_")
        and int(
            a.get("subject", {}).get("subjectId")
            or a.get("subejct", {}).get("subjectId", -1)
        ) == subject_id
    )

    print(post_count)

    post_assessments = []
    for k, a in data.items():
        if not k.startswith("post_assessment_"):
            continue
        try:
            n = int(k.rsplit("_", 1)[-1])
            sid = int(a.get("subject", {}).get("subjectId", -1))
        except (ValueError, TypeError):
            continue
        if sid == subject_id:
            post_assessments.append((n, a))
    post_assessments.sort(key=lambda x: x[0])


    if not post_assessments:
        selected = None
        pre_assessment = data.get("pre_assessment", {}).get("subject", {})
        type = "pre"
        prompt = build_initial_feedback_prompt(pre_assessment)
    elif len(post_assessments) == 1:
        selected = post_assessments[-1][1]
        pre_feedback = await db.feedback.find_one({"info.userId": user_id, "info.subject": subject}, sort=[("_id", 1)])
        pre_assessment = data.get("pre_assessment", {}).get("subject", {})
        type = "pre-post"
        prompt = build_pre_post_comparison_prompt(pre_feedback, pre_assessment, post_assessments[-1][1])
    else:
        selected = [post_assessments[-2][1], post_assessments[-1][1]]
        prev_feedback = await db.feedback.find_one({"info.userId": user_id, "info.subject": subject}, sort=[("_id", -1)])
        type = "post"
        prompt = build_post_post_comparison_prompt(prev_feedback, post_assessments[-2][1], post_assessments[-1][1])

    print("all post_tuples:", post_assessments)
    print("selected:", selected)
    print(type, prompt)

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

    #  GPT 호출
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 학습 성장 분석가입니다."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

    feedback_text = response.choices[0].message.content

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
