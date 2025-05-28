import  os
import openai
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

GPT_MODEL = "gpt-4o"
SYSTEM_ROLE = {
    "role": "system",
    "content": "당신은 친절하고 분석적인 AI 튜터입니다."
}


async def call_gpt(prompt: str) -> str:
    try:
        response = client.chat.completions.create(model=GPT_MODEL,
        messages=[SYSTEM_ROLE, {"role": "user", "content": prompt}],
        timeout=20)
        if response and response.choices:
            return response.choices[0].message.content
        else:
            return "GPT 응답이 비어있습니다."
    except openai.OpenAIError as e:
        return f"GPT 호출 중 오류 발생: {str(e)}"
