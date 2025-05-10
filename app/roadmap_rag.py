# app/roadmap_rag.py

from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import OpenAIEmbeddings

def generate_roadmap_rag(prompt: str):
    vectordb = Chroma(persist_directory="chroma_store/roadmaps", embedding_function=OpenAIEmbeddings())
    retriever = vectordb.as_retriever()

    template = """
사용자의 사전 정보와 목표:
{prompt}

위 사용자에게 적합한 학습 로드맵을 3단계로 제안해주세요.
각 단계는 제목, 설명, 이유로 구성해주세요.
"""
    final_prompt = PromptTemplate(input_variables=["prompt"], template=template)

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4o"),
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": final_prompt}
    )

    result = chain.run({"prompt": prompt})
    return result

