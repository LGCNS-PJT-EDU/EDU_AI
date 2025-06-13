from app.clients.chromadb_client import ChromaClient
from app.models.recommendation import RecommendationContent
from langchain_core.documents import Document
from app.clients.mongo_client import mongo_client

chroma_client = ChromaClient()
collection = mongo_client.recommendation_content

def sync_recommendation():
    docs = collection.find({})
    langchain_docs = []
    for doc in docs:
        content = doc.get("title", "") + "\n" + doc.get("description", "")
        metadata = {
            "user_id": doc.get("user_id", "anonymous"),
            "source": "recommendation"
        }
        langchain_docs.append(Document(page_content=content, metadata=metadata))
    chroma_client.add_documents(langchain_docs)
    print(f" 추천 콘텐츠 동기화 완료: {len(langchain_docs)}개")
