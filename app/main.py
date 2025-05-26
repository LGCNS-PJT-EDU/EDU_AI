# library
from fastapi import FastAPI

#  router import
from app.routers.pre_assessment_router import router as assessment_router
from app.routers.post_assessment_router import router as post_assessment_router
from app.routers.activity_log_router import router as activity_log_router
from app.routers.roadmap_router import router as roadmap_router
from app.routers.feedback_router import router as feedback_router
from app.routers.recommendation_router import router as recommendation_router
from app.routers.reviewnote_router import router as reviewnote_router

#  FastAPI 인스턴스 정의
app = FastAPI(
    title="AI 학습 플랫폼 API",
    version="1.0.0",
    description="진단 기반 개인 맞춤형 로드맵 및 성장 피드백 생성 API"
)

#  라우터 등록 (순서 중요)
app.include_router(assessment_router, prefix="/api/pre", tags=["사전 평가 기능 관련 API"])
app.include_router(post_assessment_router, prefix="/api/post", tags=["사후 평가 기능 관련 API"])
app.include_router(activity_log_router, prefix="/api/activity", tags=["활동 기록 기능 관련 API"])
app.include_router(roadmap_router, prefix="/api/roadmap", tags=["로드맵 기능 관련 API"])
app.include_router(feedback_router, prefix="/api/feedback", tags=["피드백 기능 관련 API"])
app.include_router(recommendation_router, prefix="/api/recommendation", tags=["추천 콘텐츠 관련 API"])
app.include_router(reviewnote_router, prefix="/ai/review" , tags=["오답 노트 관련 API"])