"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from datetime import date
import openai

from app.clients.mongodb import db
from app.models.feedback.response import FeedbackResponse
from app.services.rag_module import retrieve_similar_docs




# ----------------------  GPT 프롬프트 생성 함수 ----------------------



# ----------------------  GPT 기반 피드백 생성 API ----------------------



# ---------------------- 단일 피드백 조회 ----------------------
@router.get("/feedback/{user_id}", response_model=FeedbackResponse)
async def return_feedback(user_id: str, chapter: str = "전체"):
    query = {"user_id": user_id}
    if chapter != "전체":
        query["info.chapter"] = chapter

    doc = await db.feedback.find_one(query)
    if not doc:
        raise HTTPException(status_code=404, detail="Feedback not found")

    info = doc.get("info", {})
    content = doc.get("content", {})
    return FeedbackResponse(
        user_id=doc.get("user_id"),
        text=doc.get("text"),
        info=Info(
            userId=info.get("userId"),
            date=info.get("date"),
            subject=info.get("subject"),
            chapter=info.get("chapter")
        ),
        content=Content(
            scores=[ScoreItem(**s) for s in content.get("scores", [])],
            strengths=[StrengthWeaknessItem(**s) for s in content.get("strengths", [])],
            weaknesses=[StrengthWeaknessItem(**w) for w in content.get("weaknesses", [])]
        )
    )


# ----------------------  전체 피드백 조회 ----------------------
@router.get("/feedback", response_model=List[FeedbackResponse], response_model_by_alias=True)
async def list_feedbacks(userId: str, chapter: str = "전체"):
    query = {"info.userId": userId}
    if chapter != "전체":
        query["info.chapter"] = chapter

    docs = await db.feedback.find(query).to_list(length=1000)

    responses = []
    for doc in docs:
        info = doc.get("info", {})
        content = doc.get("content", {})
        responses.append(
            FeedbackResponse(
                user_id=doc.get("user_id"),
                text=doc.get("text"),
                info=Info(
                    userId=info.get("userId"),
                    date=info.get("date"),
                    subject=info.get("subject"),
                    chapter=info.get("chapter")
                ),
                content=Content(
                    scores=[ScoreItem(**s) for s in content.get("scores", [])],
                    strengths=[StrengthWeaknessItem(**s) for s in content.get("strengths", [])],
                    weaknesses=[StrengthWeaknessItem(**w) for w in content.get("weaknesses", [])]
                )
            )
        )

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder([r.model_dump(by_alias=True) for r in responses])
    )
"""