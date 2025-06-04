from fastapi import APIRouter, HTTPException
from typing import List

from app.models.question_model import Question
from app.clients.mongodb import MongoDBClient

router = APIRouter(prefix="/api/questions", tags=["Questions"])

# MongoDB 클라이언트 인스턴스 생성
mongodb = MongoDBClient()

@router.get("/{category}", response_model=List[Question])
async def get_questions_by_category(category: str):
    try:
        # 카테고리 컬렉션 불러오기
        collection = mongodb.get_category_collection(category)
        cursor = collection.find()

        questions = []
        async for doc in cursor:
            doc["id"] = doc.pop("_id")  # MongoDB의 _id → Pydantic용 id
            questions.append(doc)

        if not questions:
            raise HTTPException(status_code=404, detail=f"'{category}'에 해당하는 질문이 없습니다.")
        return questions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"질문을 불러오는 중 오류 발생: {str(e)}")
