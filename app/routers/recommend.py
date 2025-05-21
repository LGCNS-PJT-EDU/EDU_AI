from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

class RecommendRequest(BaseModel):
    query: str

class RecommendResponse(BaseModel):
    title: str
    url: str
    type: str
    platform: str
    duration: str
    level: str
    price: str

@router.post(
    "/recommend",
    response_model=List[RecommendResponse],
    summary="콘텐츠 추천 API",
    description="사용자 질의(query)를 기반으로 벡터 검색 후 콘텐츠를 추천합니다."
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

        results = vectordb.similarity_search_with_score(req.query, k=5)

        output = []
        for doc, score in results:
            meta = doc.metadata
            output.append(RecommendResponse(**{
                "subject_name": meta.get("subject_name",""),
                "title": meta.get("title", ""),
                "url": meta.get("url", ""),
                "type": meta.get("type", ""),
                "platform": meta.get("platform", ""),
                "duration": meta.get("duration", ""),
                "level": meta.get("level", ""),
                "price": meta.get("price", "")
            }))
        return output

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during recommendation: {str(e)}")


