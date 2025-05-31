# library
import asyncio

from fastapi import FastAPI

from app.consumer.feedback_consumer import consume_feedback
from app.kafka_admin.topic_initializer import initialize_topics
from app.producer.feedback_producer import init_producer, close_producer

from app.routers.pre_assessment_router import router as assessment_router
from app.routers.post_assessment_router import router as post_assessment_router
from app.routers.feedback_router import router as feedback_router
from app.routers.recommendation_router import router as recommendation_router

app = FastAPI(
    title="AI 학습 플랫폼 API",
    version="1.0.0",
    description="진단 기반 개인 맞춤형 로드맵 및 성장 피드백 생성 API"
)
consumer_task = None

# Kafka consumer 실행 등록
@app.on_event("startup")
async def startup_event():
    global consumer_task
    initialize_topics()
    await init_producer()
    consumer_task = asyncio.create_task(consume_feedback())

@app.on_event("shutdown")
async def shutdown_event():
    global consumer_task
    if consumer_task:
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
    await close_producer()


#  라우터 등록
app.include_router(assessment_router, prefix="/api/pre", tags=["사전 평가 기능 관련 API"])
app.include_router(post_assessment_router, prefix="/api/post", tags=["사후 평가 기능 관련 API"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["피드백 기능 관련 API"])
app.include_router(recommendation_router, prefix="/api/recommendation", tags=["추천 콘텐츠 관련 API"])