from fastapi import APIRouter, HTTPException
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from typing import List, Dict
import os

from app.clients import ai_client, chroma_client
from app.models.recommendation.request import RecommendRequest
from app.models.recommendation.response import RecommendResponse
from app.services.recommendation.recommendation import call_gpt_rerank

router = APIRouter()


@router.post("/recommend", response_model=List[RecommendResponse], summary="개인화 콘텐츠 추천 API", description="사전/사후 평가 및 진단 기반으로 사용자의 맥락에 맞는 콘텐츠 4개와 AI픽 1개를 제공합니다.")
async def recommend_content(req: RecommendRequest):
    try:
        results = chroma_client.similarity_search_with_score(req.query, k=6)

        output, content_for_gpt = [], []
        for idx, (doc, score) in enumerate(results[:4]):
            meta = doc.metadata
            item = {
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
                "type": meta.get("type", ""),
                "platform": meta.get("platform", ""),
                "duration": meta.get("duration", ""),
                "level": meta.get("level", ""),
                "price": meta.get("price", "")
            }
            content_for_gpt.append(f"{idx}: {item['title']} ({item['platform']}) - {item['url']}")
            output.append(RecommendResponse(**item))

        # 사용자 진단 정보 context string 생성
        context_str = "\n".join([
            f"강의 선호 시간: {req.user_context.get('duration_preference', 0)}",
            f"예산 선호: {req.user_context.get('price_preference', 0)}",
            f"책 선호 여부: {'예' if req.user_context.get('likes_books', 0) else '아니오'}"
        ])

        best_index = call_gpt_rerank(content_for_gpt, req.query, context_str)

        if 0 <= best_index < len(output):
            output[best_index].ai_pick = True

        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recommendation: {str(e)}")