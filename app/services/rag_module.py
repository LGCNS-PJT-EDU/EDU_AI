from app.clients.chromadb_client import ChromaClient

chroma_client = ChromaClient()  # 전역 인스턴스

def retrieve_similar_docs(query: str, top_k: int = 3):
    docs = chroma_client.similarity_search(query, k=top_k)
    return [doc.page_content for doc in docs]

def retrieve_personalized_docs(user_id: str, query: str, k=5):
    return chroma_client.similarity_search(query, k=k, metadata_filter={"user_id": user_id})

