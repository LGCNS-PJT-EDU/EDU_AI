from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.models.interview.question_model import Question
from app.clients.mongodb import MongoDBClient

router = APIRouter()
mongodb = MongoDBClient()


@router.get("/questions", response_model=List[Question])
async def get_questions_by_user_and_subject(
    user_id: str = Query(..., description="사용자 ID"),
    subject_id: int = Query(..., description="과목 ID")
):
    try:
        collection = mongodb.get_default_collection()  # 또는 통합 collection
        cursor = collection.find({"user_id": user_id, "sub_id": subject_id})

        questions = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")
            questions.append(doc)

        if not questions:
            raise HTTPException(status_code=404, detail="해당 조건의 질문이 없습니다.")
        return questions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질문 검색 중 오류 발생: {str(e)}")

