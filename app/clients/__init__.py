from .chromadb_client import ChromaClient
from .mongodb import MongoDBClient
from .openai_client import OpenAiClient


ai_client = OpenAiClient()

chroma_client = ChromaClient(
    persist_directory="chroma_store/recommend_contents",
    openai_api_key=None
)

question_client = MongoDBClient()
assessment_client = MongoDBClient(db_name="assessment")
feedback_client = MongoDBClient(db_name="feedback")
recommendation_client = MongoDBClient(db_name="recommendation")
user_client = MongoDBClient(db_name="user")
interview_client = MongoDBClient(db_name="ai_interview")

db_clients = {
    "ai_platform":    question_client,
    "assessment":     assessment_client,
    "feedback":       feedback_client,
    "recommendation": recommendation_client,
    "user":           user_client,
    "ai_interview" : interview_client,
}