from .chromadb_client import ChromaClient
from .mongodb import MongoDBClient
from .openai_client import OpenAiClient

ai_client = OpenAiClient()

# 목적별 MongoDB 클라이언트 인스턴스 생성
question_client = MongoDBClient()  # 기본값: ai_platform
assessment_client = MongoDBClient(db_name="assessment")
feedback_client = MongoDBClient(db_name="feedback")
recommendation_client = MongoDBClient(db_name="recommendation")
user_client = MongoDBClient(db_name="ai_platform")  # user_profile은 ai_platform DB에 있음
interview_client = MongoDBClient(db_name="ai_interview")

# 목적별로 분리한 클라이언트를 딕셔너리에 매핑
class MongoClientsManager:
    def __init__(self):
        self._clients = {
            "ai_platform": question_client,
            "assessment": assessment_client,
            "feedback": feedback_client,
            "recommendation": recommendation_client,
            "user": user_client,
            "ai_interview": interview_client,
        }

    def __getitem__(self, key):
        return self._clients[key]

    @property
    def recommendation_content(self):
        return self._clients["recommendation"].recommendation_content

    @property
    def recommendation_cache(self):
        return self._clients["recommendation"].recommendation_cache

    @property
    def feedback(self):
        return self._clients["feedback"].feedback

    @property
    def pre_result(self):
        return self._clients["assessment"].pre_result

    @property
    def post_result(self):
        return self._clients["assessment"].post_result

    @property
    def user_profile(self):
        return self._clients["user"].user_profile

    @property
    def interview_feedback(self):
        return self._clients["ai_interview"].interview_feedback

    @property
    def questions(self):
        return self._clients["ai_platform"].questions

    @property
    def techMap(self):
        return self._clients["ai_platform"].techMap

    @property
    def startup_log(self):
        return self._clients["ai_platform"].startup_log

# 통합 접근 객체 생성
db_clients = MongoClientsManager()

# Chroma 클라이언트
chroma_client = ChromaClient(
    persist_directory="chroma_store/recommend_contents",
    openai_api_key=None
)
