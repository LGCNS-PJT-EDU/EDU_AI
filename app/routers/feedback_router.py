from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.clients import ai_client
from app.clients.mongodb import db
from app.models.feedback.response import FeedbackResponse, Info, Feedback
from app.services.assessment.post import get_post_assessments
from app.services.common.common import subject_id_to_name
from typing import List

from app.services.feedback.builder import build_feedback
from app.services.prompt.builder import generate_feedback_prompt, build_full_prompt

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

    data = await db.user_profiles.find_one({"user_id": str(user_id)})
    if not data:
        raise HTTPException(status_code=404, detail="No User Found")

    post_assessments = await get_post_assessments(data, subject_id)
    prompt = await generate_feedback_prompt(data, post_assessments, subject, user_id)
    full_prompt = build_full_prompt(prompt, subject, user_id)

    system_msg = "당신은 한국어로 응답하는 학습 성장 분석가입니다."
    feedback_text = ai_client.create_chat_response(system_msg, full_prompt)
    feedback, info, scores = await build_feedback(data, feedback_text)

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

    return return_json