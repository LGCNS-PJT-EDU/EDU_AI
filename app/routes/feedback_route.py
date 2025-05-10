from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from datetime import date
import openai

from app.mongodb import db

router = APIRouter()

# ----------------------------- 모델 정의 -----------------------------
class FeedbackRequest(BaseModel):
    user_id: str
    pre_score: int | None = None
    post_score: int | None = None
    pre_text: str | None = None
    post_text: str | None = None

class ScoreItem(BaseModel):
    category: str
    value: int

class StrengthWeaknessItem(BaseModel):
    id: str
    description: str

class Content(BaseModel):
    scores: List[ScoreItem]
    strengths: List[StrengthWeaknessItem]
    weaknesses: List[StrengthWeaknessItem]

    model_config = {"populate_by_name": True, "populate_by_alias": True}

class Info(BaseModel):
    user_id: str = Field(..., alias="userId")
    date: date
    subject: str

    model_config = {"populate_by_name": True, "populate_by_alias": True}

class FeedbackResponse(BaseModel):
    user_id: str
    text: str
    info: Info
    content: Content

    model_config = {"populate_by_name": True, "populate_by_alias": True}

# ----------------------------- GPT 프롬프트 빌더 -----------------------------
def build_feedback_prompt(data: FeedbackRequest) -> str:
    if data.pre_score is not None and data.post_score is not None:
        gap = data.post_score - data.pre_score
        summary = f"사전 평가 점수: {data.pre_score}, 사후 평가 점수: {data.post_score}. "
        summary += f"{gap}점 향상되었습니다." if gap > 0 else (
            f"{abs(gap)}점 하락하였습니다." if gap < 0 else "점수 변화는 없습니다.")
        return f"""
당신은 학습 성장 평가 전문가입니다.

{summary}

간단한 성취도 분석과 함께 아직 부족한 개념, 동기 부여 메시지, 추가 추천 키워드를 포함해주세요.
300자 이내로 요약해주세요.
"""
    elif data.pre_text and data.post_text:
        return f"""
사전 답변: "{data.pre_text}"
사후 답변: "{data.post_text}"

두 답변을 비교해 다음 세 가지 측면에서 분석해주세요:
- 지식 깊이
- 구현 능력
- 논리적 표현력

그리고 아래 항목을 포함하세요:
1. 총평 (3줄 이내)
2. 성장 포인트 3가지
3. 개선할 점 3가지
"""
    else:
        raise ValueError("점수 또는 텍스트가 충분하지 않습니다.")

# ----------------------------- GPT 피드백 생성 -----------------------------
@router.post("/generate-feedback")
async def generate_feedback(data: FeedbackRequest):
    try:
        prompt = build_feedback_prompt(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 학습 성장 분석가입니다."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )

    feedback_text = response["choices"][0]["message"]["content"]

    await db.feedback.insert_one({
        "user_id": data.user_id,
        "text": feedback_text,
        "info": {
            "userId": data.user_id,
            "date": date.today().isoformat(),
            "subject": "frontend"  # TODO: 추후 동적 추출 가능
        },
        "content": {
            "scores": [
                {"category": "사전 평가", "value": data.pre_score or 0},
                {"category": "사후 평가", "value": data.post_score or 0}
            ],
            "strengths": [],
            "weaknesses": []
        }
    })

    return {"user_id": data.user_id, "feedback": feedback_text}

# ----------------------------- 단일 피드백 조회 -----------------------------
@router.get("/feedback/{user_id}", response_model=FeedbackResponse)
async def return_feedback(user_id: str):
    doc = await db.feedback.find_one({"user_id": user_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Feedback not found")

    info = doc.get("info", {})
    content = doc.get("content", {})

    return FeedbackResponse(
        user_id=user_id,
        text=doc.get("text"),
        info=Info(
            userId=info.get("userId"),
            date=info.get("date"),
            subject=info.get("subject")
        ),
        content=Content(
            scores=[ScoreItem(**s) for s in content.get("scores", [])],
            strengths=[StrengthWeaknessItem(**s) for s in content.get("strengths", [])],
            weaknesses=[StrengthWeaknessItem(**w) for w in content.get("weaknesses", [])]
        )
    )

# ----------------------------- 전체 피드백 목록 조회 -----------------------------
@router.get("/feedback", response_model=List[FeedbackResponse], response_model_by_alias=True)
async def list_feedbacks(userId: str):
    docs = await db.feedback.find({"info.userId": userId}).to_list(length=1000)

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
                    subject=info.get("subject")
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
