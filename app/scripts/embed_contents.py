import os
import json
import pandas as pd
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.schema import Document

# 1. 환경 변수 불러오기 및 API 키 설정
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# 2. JSON 파일 로드
with open("data/recommendation_contents.json", "r", encoding="utf-8") as f:
    contents = json.load(f)

# 3. 벡터화할 텍스트 필드 정의 (title + platform + type + duration + level + price)
def make_text(item):
    return f"{item['title']} {item['platform']} {item['type']} {item['duration']} {item['level']} {item['price']}"

# 4. Document 리스트 구성 (Chroma용)
documents = [Document(page_content=make_text(item), metadata=item) for item in contents]

# 5. 임베딩 생성 및 ChromaDB 저장
embedding = OpenAIEmbeddings()
vectordb = Chroma.from_documents(documents, embedding, persist_directory="chroma_store/contents")

# 6. 저장
vectordb.persist()
print(" 콘텐츠 임베딩 저장 완료!")
