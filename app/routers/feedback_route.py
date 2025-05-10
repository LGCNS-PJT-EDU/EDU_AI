from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List
from datetime import date
import openai

from app.clients.mongodb import db
from app.services.rag_module import retrieve_similar_docs

router = APIRouter()

# ----------------------  Pydantic 모델 ----------------------
class FeedbackRequest(BaseModel):
    user_id: str
    pre_score: int | None = None
    post_score: int | None = None
    pre_text: str | None = None
    post_text: str | None = None
    subject: str = "frontend"
    chapter: str = "전체"  # 단원명 (예: "JS", "React", "전체")

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
    chapter: str

    model_config = {"populate_by_name": True, "populate_by_alias": True}

class FeedbackResponse(BaseModel):
    user_id: str
    text: str
    info: Info
    content: Content

    model_config = {"populate_by_name": True, "populate_by_alias": True}


# ----------------------  GPT 프롬프트 생성 함수 ----------------------
def build_feedback_prompt(data: FeedbackRequest) -> str:
    if data.pre_score is not None and data.post_score is not None:
        gap = data.post_score - data.pre_score
        summary = f"사전 평가 점수: {data.pre_score}, 사후 평가 점수: {data.post_score} → 변화: {gap:+}점"

        return f"""
당신은 교육 심리 기반의 학습 진단 전문가입니다.

아래 조건을 바탕으로 전문적인 진단 보고서를 작성해주세요:

[학습 데이터]
- 과목: {data.subject}
- 단원: {data.chapter}
- {summary}

[출력 형식]
1. 성취 수준 요약 (한 문단)
2. 아직 부족한 부분과 그 원인 (구체 예시 포함)
3. 학습자의 이해를 확장할 수 있는 실전 예시/비유
4. 다음 학습 추천 키워드 3가지 (이해를 기반으로)

※ 400자 이내 요약문으로 작성해주세요.
"""
    elif data.pre_text and data.post_text:
        return f"""
당신은 교육 심리 기반의 학습 진단 전문가입니다.

[학습자 응답 비교]
- 사전 답변: "{data.pre_text}"
- 사후 답변: "{data.post_text}"
- 과목: {data.subject}, 단원: {data.chapter}

다음 기준으로 분석해주세요:
1. 지식 수준의 확장 (이전 대비 무엇을 알게 되었는지)
2. 개념 오해 또는 불완전한 설명 요소
3. 실제 상황에서의 적용 가능성 (구현 관점)
4. 추천 보완 개념 3가지 (이해 기반 추천)

※ 전체 400자 이내의 평가 요약문으로 작성해주세요.
"""
    else:
        raise ValueError("점수 또는 텍스트가 충분하지 않습니다.")


# ----------------------  GPT 기반 피드백 생성 API ----------------------
@router.post("/generate-feedback")
async def generate_feedback(data: FeedbackRequest):
    try:
        base_prompt = build_feedback_prompt(data)

        # RAG 검색 통합
        context_docs = retrieve_similar_docs(data.post_text or data.pre_text or "")
        context_text = "\n".join(context_docs)

        # 프롬프트 최종 구성
        full_prompt = f"""
[RAG 기반 유사 학습 정보]
{context_text}

[사용자 피드백 요청]
{base_prompt}
"""
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    #  GPT 호출
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "당신은 학습 성장 분석가입니다."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=800
    )
    feedback_text = response['choices'][0]['message']['content']

    #  MongoDB 저장
    await db.feedback.insert_one({
        "user_id": data.user_id,
        "text": feedback_text,
        "info": {
            "userId": data.user_id,
            "date": date.today().isoformat(),
            "subject": data.subject,
            "chapter": data.chapter
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
