import json
import openai
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List

from app.clients import db_clients
from app.models.interview.question_model import InterviewQuestion
from app.services.common.common import subject_id_to_name
from app.services.interview.bulider import get_questions_by_sub_id
from app.models.interview.evaluation_model import EvaluationRequest
from app.services.interview.evaluator import evaluate_answer_with_rag
from app.utils.embed import embed_to_chroma

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
@router.post("/evaluate", summary="면접 답변 평가 (복수 개)", response_model=List[dict])
async def evaluate_with_rag_and_embed(
    user_id: str = Query(..., description="사용자 ID"),
    requests: List[EvaluationRequest] = Body(...)
):
    try:
        results = []

        for request in requests:
            result = await evaluate_answer_with_rag(
                user_id=user_id,
                question=request.interviewContent,
                user_answer=request.userReply
            )
            results.append(result)

            embed_to_chroma(
                user_id=user_id,
                content=request.userReply,
                source="interview",
                source_id=str(request.interviewId)
            )

        return results

    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="GPT 응답이 올바른 JSON이 아닙니다.")
    except openai.APIConnectionError:
        raise HTTPException(status_code=503, detail="OpenAI API 연결 실패")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"오류 발생: {str(e)}")
