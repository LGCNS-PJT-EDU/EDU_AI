import json
import openai
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List
from app.clients import interview_client
from app.clients import db_clients
from app.models.interview.question_model import InterviewQuestion
from app.services.common.common import subject_id_to_name
from app.services.interview.bulider import get_questions_by_sub_id
from app.models.interview.evaluation_model import EvaluationRequest
from app.services.interview.evaluator import evaluate_answer_with_rag
from app.utils.embed import embed_to_chroma
from bson import ObjectId


router = APIRouter(tags=["인터뷰 면접 기능 관련 API"])


#  면접 질문 조회 API
@router.get("/questions", response_model=List[InterviewQuestion], summary="면접 질문 조회")
async def get_questions(
    user_id: str,
    subject_id: int,
    num: int = Query(1, description="질문 개수")
):
    try:
        subject_name = await subject_id_to_name(subject_id)
        questions = await get_questions_by_sub_id(subject_name, num)
        return questions
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질문 검색 중 오류 발생: {str(e)}")


@router.post("/evaluate", summary="면접 답변 평가 및 저장 (복수 개)", response_model=List[dict])
async def evaluate_with_rag_and_embed(
    user_id: str = Query(..., description="사용자 ID"),
    requests: List[EvaluationRequest] = Body(...)
):
    try:
        evaluations = []

        for request in requests:
            # 1. GPT 평가
            evaluation_result = await evaluate_answer_with_rag(
                user_id=user_id,
                question=request.interviewContent,
                user_answer=request.userReply
            )

            # 2. Chroma 임베딩
            embed_to_chroma(
                user_id=user_id,
                content=request.userReply,
                source="interview",
                source_id=str(request.interviewId)
            )

            # 3. MongoDB 저장 (기록은 유지)
            doc = {
                "user_id": user_id,
                "interview_id": request.interviewId,
                "interview_content": request.interviewContent,
                "user_reply": request.userReply,
                "evaluation": evaluation_result
            }
            await interview_client.interview_feedback.insert_one(doc)

            # 4. evaluation만 리스트로 추가
            evaluations.append(evaluation_result)

        # 전체 문서 대신 evaluation 리스트만 반환
        return evaluations

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")


