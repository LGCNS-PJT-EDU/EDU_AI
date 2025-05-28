from typing import List, Dict

import openai

from app.clients import ai_client, chroma_client


def call_gpt_rerank(contents: List[str], context: str) -> int:
    prompt = f"""
        사용자 정보:
            {context}
    
        아래 콘텐츠 중 가장 적합한 1개의 index 번호만 숫자로 출력해 주세요:
            {contents}
    """

    system_prompt = "당신은 교육 추천 전문가입니다."
    try:
        idx_str = ai_client.create_chat_response(system_prompt, prompt).strip()
        return int(idx_str)
    except:
        return 0


def explain_reason_with_rag(title: str, user_context: str):
    vectordb = chroma_client

    try:
        similar_docs = vectordb.similarity_search(title, k=6)
        context_text = "\n".join([doc.page_content for doc in similar_docs])

        prompt = f"""
        사용자 맥락: {user_context}
        추천 콘텐츠 제목: {title}
        관련 설명들: {context_text}

        이 콘텐츠가 추천된 이유를 간단히 2~3문장으로 설명해 주세요.
        """

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 교육 추천 설명 전문가입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("GPT 설명 실패:", e)
        return "이 콘텐츠는 사용자의 관심 조건에 부합하여 추천되었습니다."