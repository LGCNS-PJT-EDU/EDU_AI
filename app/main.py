# library
import asyncio
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

# FastAPI 인스턴스 먼저 정의
app = FastAPI(
    title="AI 학습 플랫폼 API",
    version="1.0.0",
    description="진단 기반 개인 맞춤형 로드맵 및 성장 피드백 생성 API"
)

# Prometheus AIOps 미들웨어 삽입 (metrics 라우터 자동 생성)
Instrumentator().instrument(app).expose(app)

# Kafka 관련 기능
from app.consumer.feedback_consumer import consume_feedback
from app.consumer.recommendation_consumer import consume_recommend
from app.kafka_admin.topic_initializer import initialize_topics
from app.producer.feedback_producer import init_feedback_producer, close_feedback_producer
from app.producer.recommendation_producer import close_recommendation_producer, init_recommendation_producer

# 라우터 등록
from app.routers.pre_assessment_router import router as assessment_router
from app.routers.post_assessment_router import router as post_assessment_router
from app.routers.feedback_router import router as feedback_router
from app.routers.recommendation_router import router as recommendation_router
from app.routers.question_router import router as question_router
from app.routers.chroma_status_router import router as chroma_status_router
from app.routers.status_router import router as status_router


# 라우터 등록
app.include_router(assessment_router, prefix="/api/pre", tags=["사전 평가 기능 관련 API"])
app.include_router(post_assessment_router, prefix="/api/post", tags=["사후 평가 기능 관련 API"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["피드백 기능 관련 API"])
app.include_router(recommendation_router, prefix="/api/recommendation", tags=["추천 콘텐츠 관련 API"])
app.include_router(question_router, prefix="/api/question", tags=["인터뷰 면접 기능 관련 API"])
app.include_router(chroma_status_router, prefix="/api/chroma", tags=["ChromaDB 상태 점검 API"])
app.include_router(status_router, prefix="/api", tags=["AIOps 상태 모니터링"])

# Kafka consumer 실행 등록
feedback_consumer_task = None
recom_consumer_task = None

@app.on_event("startup")
async def startup_event():
    global feedback_consumer_task, recom_consumer_task
    initialize_topics()
    await init_feedback_producer()
    await init_recommendation_producer()
    feedback_consumer_task = asyncio.create_task(consume_feedback())
    recom_consumer_task = asyncio.create_task(consume_recommend())

@app.on_event("shutdown")
async def shutdown_event():
    global feedback_consumer_task, recom_consumer_task
    if feedback_consumer_task:
        feedback_consumer_task.cancel()
        try:
            await feedback_consumer_task
        except asyncio.CancelledError:
            pass
    await close_feedback_producer()

    if recom_consumer_task:
        recom_consumer_task.cancel()
        try:
            await recom_consumer_task
        except asyncio.CancelledError:
            pass
        await close_recommendation_producer()


