# app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
import openai
import os

#  라우터들 먼저 import
from app.routes.assessment import router as assessment_router
from app.routes.post_assessment import router as post_assessment_router
from app.routes.activity_log import router as activity_log_router
from app.routes.roadmap_route import router as roadmap_router
from app.routes.feedback_route import router as feedback_router

#  환경 변수 및 OpenAI 키 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

#  FastAPI 인스턴스 정의
app = FastAPI(
    title="AI 학습 플랫폼 API",
    version="1.0.0",
    description="진단 기반 개인 맞춤형 로드맵 및 성장 피드백 생성 API"
)

#  라우터 등록 (순서 중요)
app.include_router(assessment_router, prefix="/api/v1")
app.include_router(post_assessment_router, prefix="/api/v1")
app.include_router(activity_log_router, prefix="/api/v1")
app.include_router(roadmap_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
