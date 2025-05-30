from openai import OpenAI
from app.clients import chroma_client

client = OpenAI()

def explain_reason_with_rag(title: str, user_context: str) -> str:
    vectordb = chroma_client
    try:
        docs_with_scores = vectordb.similarity_search_with_score(title, k=6)
        context_text = "\n".join([doc.page_content for doc, _ in docs_with_scores])

        prompt = f"""
        사용자 맥락: {user_context}
        추천 콘텐츠 제목: {title}
        관련 설명들: {context_text}

        이 콘텐츠가 추천된 이유를 간단히 2~3문장으로 설명해 주세요.
        """

        response = client.chat.completions.create(
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
