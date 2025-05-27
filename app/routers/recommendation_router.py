from fastapi import APIRouter, HTTPException
from typing import List

from app.clients import chroma_client
from app.models.recommendation.request import UserPreference
from app.models.recommendation.response import RecommendationResponse
from app.services.common.common import get_user, subject_id_to_name
from app.services.recommendation.recommendation import call_gpt_rerank

router = APIRouter()


@router.post("/recommend", response_model=List[RecommendationResponse], summary="개인화 콘텐츠 추천 API", description="사전/사후 평가 및 진단 기반으로 사용자의 맥락에 맞는 콘텐츠 4개와 AI픽 1개를 제공합니다.")
async def recommend_content(user_id: str, subject_id: int):
    user = await get_user(user_id)
    username = user.get("name")
    subject = await subject_id_to_name(subject_id)

    print(user)
    print(subject)

    query_str = f"{username}의 {subject}에 대한 추천 컨텐츠를 선정합니다."
    raw_prefs = user.get("preferences", {})
    prefs = UserPreference(
        level=user.get("level"),
        duration=raw_prefs.get("duration", 0),
        price=raw_prefs.get("price", 0),
        is_prefer_book=raw_prefs.get("is_prefer_book", False),
    )

    print(query_str)
    print(prefs)

    try:
        result = chroma_client.similarity_search_with_score(query_str, k=6)
        filtered = [(d,s) for d,s in result if d.metadata.get("subjectId")==subject_id][:6]

        output, content_for_gpt = [], []
        for idx, (doc, score) in enumerate(filtered[:4]):
            meta = doc.metadata
            item = {
                "contentId": meta.get("contentId"),
                "subjectId": meta.get("subjectId"),
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
                "type": meta.get("type", ""),
                "platform": meta.get("platform", ""),
                "duration": meta.get("duration", ""),
                "price": meta.get("price", "")
            }
            content_for_gpt.append(f"{idx}: {item['title']} ({item['platform']}) - {item['url']}")
            output.append(RecommendationResponse(**item))

        context_str = "\n".join([
            f"강의 선호 시간: {prefs.duration}",
            f"예산 선호: {prefs.price}",
            f"책 선호 여부: {prefs.is_prefer_book}",
        ])

        best_index =    call_gpt_rerank(content_for_gpt, query_str, context_str)

        if 0 <= best_index < len(output):
            output[best_index].is_ai_recommendation = True

        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recommendation: {str(e)}")