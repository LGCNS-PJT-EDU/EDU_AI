# app/scripts/migrate_mongo_to_chroma.py
import os
from pymongo import MongoClient
from bson.objectid import ObjectId
from langchain_core.documents import Document
from app.clients.chromadb_client import ChromaClient
from dotenv import load_dotenv

load_dotenv()

mongo_client = MongoClient(os.getenv("MONGO_URI"))
collection = mongo_client["ai_interview"]["interview_contents"]
chroma_client = ChromaClient()

def migrate_all_user_docs():
    user_ids = collection.distinct("user_id")
    total = 0

    for user_id in user_ids:
        docs = collection.find({"user_id": user_id})
        langchain_docs = []

        for doc in docs:
            content = doc.get("content", "")
            if not content:
                continue
            metadata = {"user_id": user_id, "source_id": str(doc["_id"])}
            langchain_docs.append(Document(page_content=content, metadata=metadata))

        if langchain_docs:
            chroma_client.add_documents(langchain_docs)
            print(f" user_id={user_id}: {len(langchain_docs)}개 삽입")
            total += len(langchain_docs)

    print(f" 전체 삽입 완료: 총 {total}개 문서")

if __name__ == "__main__":
    migrate_all_user_docs()