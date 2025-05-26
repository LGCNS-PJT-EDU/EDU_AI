from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from typing import List, Dict
import os
from dotenv import load_dotenv
import openai

from app.models.recommend.request import RecommendRequest
from app.models.recommend.response import RecommendResponse

load_dotenv()

router = APIRouter()


#  GPT를 통한 AI Pick 결정 함수
def call_gpt_rerank(contents: List[Dict], query: str, context: str) -> int:
    prompt = f"""
다음은 사용자의 학습 맥락입니다:
{context}

사용자의 학습 목표와 관련하여, 아래 콘텐츠들 중 가장 적합한 하나를 골라주세요:
{contents}

가장 적합한 콘텐츠의 번호(index)를 하나의 숫자로만 출력해주세요.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 교육 추천 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=10
        )
        idx_str = response.choices[0].message.content.strip()
        return int(idx_str)
    except:
        return 0

@router.post(
    "/recommend",
    response_model=List[RecommendResponse],
    summary="개인화 콘텐츠 추천 API",
    description="사전/사후 평가 및 진단 기반으로 사용자의 맥락에 맞는 콘텐츠 4개와 AI픽 1개를 제공합니다."
)
async def recommend_content(req: RecommendRequest):
    try:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY not found")

        embedding = OpenAIEmbeddings(openai_api_key=openai_key)
        vectordb = Chroma(
            persist_directory="chroma_store/contents",
            embedding_function=embedding
        )

        results = vectordb.similarity_search_with_score(req.query, k=6)

        output = []
        content_for_gpt = []
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


