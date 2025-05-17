from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import Document

embedding = OpenAIEmbeddings()
db = Chroma(persist_directory="chroma_store/explanation", embedding_function=embedding)

# 1. 설명 저장 함수
def save_explanation_to_chroma(user_id: str, explanation: str, metadata: dict):
    doc = Document(
        page_content=explanation,
        metadata={"user_id": user_id, **metadata}
    )
    db.add_documents([doc])

# 2. 유사 설명 검색 함수
def search_similar_explanations(query: str, top_k: int = 3):
    results = db.similarity_search(query, k=top_k)
    return [doc.page_content for doc in results]

