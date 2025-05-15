# app/roadmap.py

from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

embedding = OpenAIEmbeddings()

# 신규 기능: 사용자별 GPT 설명 결과 벡터 저장
def save_explanation_to_chroma(user_id: str, explanation: str, metadata: dict):
    db = Chroma(persist_directory="chroma_store/explanation", embedding_function=embedding)

    doc = Document(
        page_content=explanation,
        metadata={"user_id": user_id, **metadata}
    )
    db.add_documents([doc])

