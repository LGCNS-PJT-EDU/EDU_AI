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
    [사용자 요청]
    {question}

    [참고 문서]
    {context}

    위 사용자에게 적합한 학습 로드맵을 3단계로 제안해주세요.
    각 단계는 제목, 설명, 이유로 구성해주세요.
    """

    # context + question 두 개를 필수로 넣어야 함
    final_prompt = PromptTemplate(input_variables=["context", "question"], template=template)

    chain = RetrievalQA.from_chain_type(
        llm=ChatOpenAI(model_name="gpt-4o"),
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": final_prompt}
    )

    # prompt는 'question'으로 전달
    result = chain.run({"question": prompt})
    return result


