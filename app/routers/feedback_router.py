from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse

from app.clients import ai_client
from app.clients import db_clients
from app.models.feedback.response import FeedbackResponse, Info, Feedback
from app.services.assessment.post import get_post_assessments
from app.services.common.common import subject_id_to_name
from typing import List

from app.services.feedback.builder import build_feedback
from app.services.prompt.builder import generate_feedback_prompt, build_full_prompt, calculate_chapter_scores
from app.utils.embed import embed_to_chroma

router = APIRouter()

feedback_db = db_clients["feedback"]
assessment_db = db_clients["assessment"]
user_db = db_clients["user"]

@router.get("", response_model=List[FeedbackResponse], response_model_by_alias=True, summary="지정한 사용자의 피드백을 반환", description="해당 유저의 전체 피드백을 반환한다.")
async def list_feedbacks(userId: str):
    target = feedback_db.feedback.find({"info.userId": userId})
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


async def generate_feedback(user_id, subject_id, feedback_type, nth):
    user = await user_db.user_profile.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="사용자 정보를 찾을 수 없습니다.")

    subject = await subject_id_to_name(subject_id)

    base_prompt, max_score = await generate_feedback_prompt(user_id, subject, subject_id, feedback_type.upper(), nth)
    full_prompt = build_full_prompt(base_prompt, subject, user_id, max_score)

    system_msg = "당신은 한국어로 응답하는 학습 성장 분석가입니다."
    feedback_text = ai_client.create_chat_response(system_msg, full_prompt)
    feedback, info, scores = await build_feedback(user, feedback_text, max_score)
    print("DEBUG - feedback:", feedback)
    print("DEBUG - info:", info)
    print("DEBUG - scores:", scores)

    #  Chroma 자동 삽입
    embed_to_chroma(
        user_id=user_id,
        content=feedback_text,
        source="feedback",
        source_id=subject
    )

    await feedback_db.feedback.insert_one({
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