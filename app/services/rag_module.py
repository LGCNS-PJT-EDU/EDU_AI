# app/services/rag_module.py
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.clients.chromadb_client import ChromaClient

CHROMA_DIR = "chroma_store"
chroma_client = ChromaClient(CHROMA_DIR)

# 일반 검색
def init_vector_store():
    embedding = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
    return vectordb

def retrieve_similar_docs(query: str, top_k: int = 3):
    vectordb = init_vector_store()
    docs = vectordb.similarity_search(query, k=top_k)
    return [doc.page_content for doc in docs]

#  개인화 검색 함수
def retrieve_personalized_docs(user_id: str, query: str, k=5):
    return chroma_client.client.similarity_search(
        query=query,
        k=k,
        filter={"user_id": user_id}
    )

