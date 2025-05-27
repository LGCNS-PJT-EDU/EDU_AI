from fastapi import APIRouter, HTTPException
from typing import List, Tuple

from app.clients import chroma_client
from app.models.recommendation.request import UserPreference
from app.models.recommendation.response import RecommendationResponse
from app.services.common.common import get_user, subject_id_to_name
from app.services.recommendation.recommendation import call_gpt_rerank

router = APIRouter()


def rule(meta: dict, prefs: UserPreference):
    if prefs.duration and isinstance(meta.get("duration"), int):
        if meta["duration"] > prefs.duration:
            return False

    if prefs.price and isinstance(meta.get("price"), int):
        if meta["price"] > prefs.price:
            return False

    if prefs.is_prefer_book:
        if not meta.get("is_prefer_book"):
            return False

    return True


@router.post("/recommend", response_model=List[RecommendationResponse], summary="개인화 콘텐츠 추천 API", description="사전/사후 평가 및 진단 기반으로 사용자의 맥락에 맞는 콘텐츠 4개와 AI픽 1개를 제공합니다.")
async def recommend_content(user_id: str, subject_id: int):
    user = await get_user(user_id)
    subject = await subject_id_to_name(subject_id)

    query_str = f"{user}의 {subject}에 대한 추천 컨텐츠를 선정합니다."
    raw_prefs = user.get("preferences", {})
    prefs = UserPreference(
        level=user.get("level", "Not_Defined"),
        duration=raw_prefs.get("duration", 0),
        price=raw_prefs.get("price", 0),
        is_prefer_book=raw_prefs.get("is_prefer_book", False),
    )

    try:
        results: List[Tuple] = chroma_client.similarity_search_with_score(query_str, k=6)
        candidates = [
                         (doc, score) for doc, score in results
                         if doc.metadata.get("subjectId") == subject_id
                            and rule(doc.metadata, prefs)
                     ][:6]

        output: List[RecommendationResponse] = []
        content_for_gpt = []
        for idx, (doc, _) in enumerate(candidates[:4]):
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

        best_index = call_gpt_rerank(content_for_gpt, query_str, context_str)

        if 0 <= best_index < len(output):
            output[best_index].is_ai_recommendation = True

        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recommendation: {str(e)}")