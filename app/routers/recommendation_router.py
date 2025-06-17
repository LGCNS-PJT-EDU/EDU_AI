#  app/routers/recommendation_router.py 수정 예시
import asyncio

from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime

from app.clients import chroma_client, db_clients
from app.models.recommendation.request import UserPreference
from app.models.recommendation.response import RecommendationResponse
from app.services.common.common import get_user, subject_id_to_name
from app.services.recommendation.rag_explainer import explain_reason_with_rag
from app.services.recommendation.reranker import call_gpt_rerank
from app.utils.embed import embed_to_chroma

router = APIRouter()

vectordb = chroma_client
recommendation_db = db_clients["recommendation"]

recommendation_collection = recommendation_db.recommendation_content
cache_collection = recommendation_db.recommendation_cache

@router.post("", response_model=List[RecommendationResponse], summary="개인화 콘텐츠 추천 API", description="사전/사후 평가 및 진단 기반으로 사용자의 맥락에 맞는 콘텐츠 4개와 AI픽 1개를 제공합니다.")
async def recommend_content(user_id: str, subject_id: int):
    user = await get_user(user_id)
    subject = await subject_id_to_name(subject_id)
    all_levels = user.get("level", {})

    raw_prefs = user.get("preferences", {})
    prefs = UserPreference(
        level=all_levels.get(str(subject_id), "Not_Defined"),
        duration=raw_prefs.get("duration", 0),
        price=raw_prefs.get("price", 0),
        is_prefer_book=raw_prefs.get("is_prefer_book", False),
    )

    try:
        content_types = ["책"] if prefs.is_prefer_book else ["동영상", "블로그"]
        candidates = await recommendation_collection.find({
            "sub_id": subject_id,
            "content_type": {"$in": content_types},
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
        log = []

        for idx, item in enumerate(candidates[:4]):
            title = item.get("content_title")
            cached = await cache_collection.find_one({
                "title": title,
                "user_context": context_str
            })

            if cached:
                reason = cached["cached_reason"]
            else:
                reason = explain_reason_with_rag(title, context_str)
                log.append({
                    "title": title,
                    "user_context": context_str,
                    "cached_reason": reason,
                    "cached_at": datetime.utcnow()
                })

            #  Chroma 삽입
            content_text = f"{item['content_title']} {item['content_platform']} {item['content_type']}"
            embed_to_chroma(user_id=user_id, content=content_text, source="recommendation", source_id=str(item["_id"]))

            summary = f"{idx}: {title} ({item['content_platform']}) - {item['content_url']}"
            content_for_gpt.append(summary)

            results.append({
                "contentId": item["total_content_id"],
                "subjectId": item["sub_id"],
                "title": item["content_title"],
                "url": item["content_url"],
                "type": item["content_type"],
                "platform": item["content_platform"],
                "duration": item["content_duration"],
                "price": item["content_price"],
                "isAiRecommendation": False,
                "comment": reason
            })

        best_index = call_gpt_rerank(content_for_gpt, context_str)
        if 0 <= best_index < len(results):
            results[best_index]["isAiRecommendation"] = True

        if log:
            await cache_collection.insert_many(log)

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recommendation: {str(e)}")
