from fastapi import APIRouter, HTTPException
from typing import List

from app.clients import chroma_client, mongo_client
from app.models.recommendation.request import UserPreference
from app.models.recommendation.response import RecommendationResponse
from app.services.common.common import get_user, subject_id_to_name
from app.services.recommendation.recommendation import call_gpt_rerank, explain_reason_with_rag

router = APIRouter()

vectordb = chroma_client
recommend_collection = mongo_client.recommend_contents

@router.post("", response_model=List[RecommendationResponse], summary="개인화 콘텐츠 추천 API", description="사전/사후 평가 및 진단 기반으로 사용자의 맥락에 맞는 콘텐츠 4개와 AI픽 1개를 제공합니다.")
async def recommend_content(user_id: str, subject_id: int):
    user = await get_user(user_id)
    subject = await subject_id_to_name(subject_id)

    raw_prefs = user.get("preferences", {})
    prefs = UserPreference(
        level=user.get("level", "Not_Defined"),
        duration=raw_prefs.get("duration", 0),
        price=raw_prefs.get("price", 0),
        is_prefer_book=raw_prefs.get("is_prefer_book", False),
    )

    try:
        candidates = await recommend_collection.find({
            "sub_id": subject_id,
            "content_type": prefs.is_prefer_book
        }).limit(6).to_list(length=6)

        if not candidates:
            raise HTTPException(status_code=404, detail="추천 콘텐츠 없음")

        context_str = "\n".join([
            f"선호 시간: {prefs.duration}분",
            f"예산: {prefs.price}원",
            f"책 선호: {'예' if prefs.is_prefer_book else '아니오'}"
        ])

        results: List[RecommendationResponse] = []
        content_for_gpt: List[str] = []

        for idx, item in enumerate(candidates[:4]):
            _reason = explain_reason_with_rag(item["content_title"], context_str)
            summary = f"{idx}: {item['content_title']} ({item['content_platform']}) - {item['content_url']}"
            content_for_gpt.append(summary)

            results.append({
                "contentId": item.get("contentId"),
                "subjectId": item.get("subjectId"),
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "type": item.get("type", ""),
                "platform": item.get("platform", ""),
                "duration": item.get("duration", ""),
                "price": item.get("price", "")
            })

        best_index = call_gpt_rerank(content_for_gpt, context_str)
        if 0 <= best_index < len(results):
            results[best_index]["ai_pick"] = True
            results[best_index]["ai_pick_comment"] = "이 콘텐츠는 AI가 가장 적합하다고 판단한 추천입니다!"

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recommendation: {str(e)}")