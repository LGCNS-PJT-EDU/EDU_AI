# app/services/roadmap_vectorstore.py
import os
from typing import Union, List

from dotenv import load_dotenv
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)


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
