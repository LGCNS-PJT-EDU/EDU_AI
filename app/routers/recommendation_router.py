#  1. 필요한 패키지 설치 (처음 1회)
# pip install fastapi uvicorn langchain openai pymongo chromadb python-dotenv

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
import openai
import os
from dotenv import load_dotenv

load_dotenv()

#  ChromaDB 임베딩 연결 (최초 1회만 실행)
vectordb = Chroma(
    persist_directory="chroma_store/recommend_contents",
    embedding_function=OpenAIEmbeddings()
)

# MongoDB 연결
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_client = MongoClient("mongodb://54.180.4.224:27017")  # 또는 .env에서 MONGO_URI 사용
db = mongo_client["ai_platform"]
recommend_collection = db["recommend_contents"]  # ✅ 이 줄이 꼭 필요!



#  요청 모델
class RecommendRequest(BaseModel):
    sub_id: int
    preferred_type: str
    duration_preference: int
    user_context: dict  # price_preference, likes_books 등 포함

#  GPT rerank (AI Pick 선정)
def call_gpt_rerank(contents: list[str], context: str) -> int:
    prompt = f"""
사용자 정보:
{context}

아래 콘텐츠 중 가장 적합한 1개의 index 번호만 숫자로 출력해 주세요:
{contents}
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
        return int(response.choices[0].message.content.strip())
    except:
        return 0

#  추천 설명 생성 함수 (Chroma + GPT)
def explain_reason_with_rag(title: str, user_context: str) -> str:
    try:
        similar_docs = vectordb.similarity_search(title, k=6)
        context_text = "\n".join([doc.page_content for doc in similar_docs])

        prompt = f"""
        사용자 맥락: {user_context}
        추천 콘텐츠 제목: {title}
        관련 설명들: {context_text}

        이 콘텐츠가 추천된 이유를 간단히 2~3문장으로 설명해 주세요.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 교육 추천 설명 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("GPT 설명 실패:", e)
        return "이 콘텐츠는 사용자의 관심 조건에 부합하여 추천되었습니다."

#  FastAPI 라우터 정의
router = APIRouter()

@router.post("/recommend-with-reason")
async def recommend_with_reason(req: RecommendRequest):
    try:
        #  MongoDB에서 콘텐츠 필터링
        candidates = list(recommend_collection.find({
            "sub_id": req.sub_id,
            "content_type": req.preferred_type
        }).limit(6))

        if not candidates:
            raise HTTPException(status_code=404, detail="추천 콘텐츠 없음")

        #  사용자 맥락 문자열 생성
        context_str = "\n".join([
            f"선호 시간: {req.duration_preference}분",
            f"예산: {req.user_context.get('price_preference')}",
            f"책 선호: {'예' if req.user_context.get('likes_books') else '아니오'}"
        ])

        results = []
        content_for_gpt = []

        #  각 콘텐츠에 대해 GPT 설명 생성 & AI Pick 후보 구성
        for idx, item in enumerate(candidates[:4]):
            reason = explain_reason_with_rag(item["content_title"], context_str)
            summary = f"{idx}: {item['content_title']} ({item['content_platform']}) - {item['content_url']}"
            content_for_gpt.append(summary)

            results.append({
                "contentId": item.get("total_content_id"),
                "title": item.get("content_title"),
                "url": item.get("content_url"),
                "platform": item.get("content_platform"),
                "type": item.get("content_type"),
                "reason": reason,
                "ai_pick": False,
                "ai_pick_comment": None
            })

        #  GPT가 AI Pick 하나 고르도록 요청
        best_index = call_gpt_rerank(content_for_gpt, context_str)
        if 0 <= best_index < len(results):
            results[best_index]["ai_pick"] = True
            results[best_index]["ai_pick_comment"] = "이 콘텐츠는 AI가 가장 적합하다고 판단한 추천입니다!"

        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"추천 중 오류 발생: {str(e)}")
