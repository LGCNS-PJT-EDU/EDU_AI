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


#  면접 답변 평가 API (복수 개 요청 처리 + Chroma 임베딩)

@router.post("/evaluate", summary="면접 답변 평가 및 저장 (복수 개)", response_model=dict)
async def evaluate_with_rag_and_embed(
    user_id: str = Query(..., description="사용자 ID"),
    requests: List[EvaluationRequest] = Body(...)
):
    try:
        inserted_ids = []

        for request in requests:
            evaluation_result = await evaluate_answer_with_rag(
                user_id=user_id,
                question=request.interviewContent,
                user_answer=request.userReply
            )

            embed_to_chroma(
                user_id=user_id,
                content=request.userReply,
                source="interview",
                source_id=str(request.interviewId)
            )

            doc = {
                "user_id": user_id,
                "interview_id": request.interviewId,
                "interview_content": request.interviewContent,
                "user_reply": request.userReply,
                "evaluation": evaluation_result,
            }
            result = await interview_client.interview_feedback.insert_one(doc)
            inserted_ids.append(result.inserted_id)

        # MongoDB에서 방금 삽입한 결과들을 다시 조회
        cursor = interview_client.interview_feedback.find({"_id": {"$in": inserted_ids}})
        saved_docs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # ObjectId → 문자열 변환
            saved_docs.append(doc)

        return {
            "results": saved_docs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")


@router.get("/evaluate/history", summary="지정된 평가 ID 목록 조회", response_model=List[dict])
async def get_evaluation_by_ids(
    ids: str = Query(..., description="ObjectId 문자열들을 쉼표로 구분 (예: id1,id2,id3)")
):
    try:
        object_ids = [ObjectId(id_str) for id_str in ids.split(",")]
        cursor = interview_client.interview_feedback.find({"_id": {"$in": object_ids}})
        results = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"평가 결과 조회 실패: {str(e)}")



