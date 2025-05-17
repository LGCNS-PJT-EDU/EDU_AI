# app/services/roadmap_vectorstore.py

from typing import Union, List
from langchain.schema import Document
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings

embedding = OpenAIEmbeddings()


def save_explanations_to_chroma(
    user_id: str,
    explanations: Union[str, List[str]],
    metadata: dict
):

    if isinstance(explanations, str):
        explanations = [explanations]


    db = Chroma(
        persist_directory="chroma_store/explanation",
        embedding_function=embedding
    )


    docs = [
        Document(
            page_content=ex,
            metadata={"user_id": user_id, **metadata}
        )
        for ex in explanations
    ]

    db.add_documents(docs)
    db.persist()
