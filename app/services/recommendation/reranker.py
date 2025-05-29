from typing import List
from app.clients import ai_client

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
