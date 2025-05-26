from typing import List, Dict

from app.clients import ai_client


def call_gpt_rerank(contents: List[Dict], query: str, context: str) -> int:
    prompt = f"""
        다음은 사용자의 학습 맥락입니다:
        {context}

        사용자의 학습 목표와 관련하여, 아래 콘텐츠들 중 가장 적합한 하나를 골라주세요:
        {contents}

        가장 적합한 콘텐츠의 번호(index)를 하나의 숫자로만 출력해주세요.
    """

    system_prompt = "당신은 교육 추천 전문가입니다."
    try:
        idx_str = ai_client.create_chat_response(system_prompt, prompt).strip()
        return int(idx_str)
    except:
        return 0