# library
import asyncio

from fastapi import FastAPI
from app.consumer.feedback_consumer import start_feedback_consumer_thread
from app.kafka_admin.topic_initializer import initialize_topics

#  router import
from app.routers.pre_assessment_router import router as assessment_router
from app.routers.post_assessment_router import router as post_assessment_router
from app.routers.activity_log_router import router as activity_log_router
from app.routers.roadmap_router import router as roadmap_router
from app.routers.feedback_router import router as feedback_router

#  FastAPI 인스턴스 정의
app = FastAPI(
    title="AI 학습 플랫폼 API",
    version="1.0.0",
    description="진단 기반 개인 맞춤형 로드맵 및 성장 피드백 생성 API"
)

# Kafka consumer 실행 등록
@app.on_event("startup")
async def startup_event():
    initialize_topics()
    start_feedback_consumer_thread()

#  라우터 등록 (순서 중요)
app.include_router(assessment_router, prefix="/api/pre", tags=["사전 평가 기능 관련 API"])
app.include_router(post_assessment_router, prefix="/api/post", tags=["사후 평가 기능 관련 API"])
app.include_router(activity_log_router, prefix="/api/activity", tags=["활동 기록 기능 관련 API"])
app.include_router(roadmap_router, prefix="/api/roadmap", tags=["로드맵 기능 관련 API"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["피드백 기능 관련 API"])