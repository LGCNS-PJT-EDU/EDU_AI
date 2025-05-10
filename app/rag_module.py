# app/rag_module.py

from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

CHROMA_DIR = "chroma_store"

# 벡터 검색기 초기화
def init_vector_store():
    embedding = OpenAIEmbeddings()
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding)
    return vectordb

# 쿼리에 대한 유사 문서 검색
def retrieve_similar_docs(query: str, top_k: int = 3):
    vectordb = init_vector_store()
    docs = vectordb.similarity_search(query, k=top_k)
    return [doc.page_content for doc in docs]
