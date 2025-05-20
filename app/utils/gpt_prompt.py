import  os
import openai

GPT_MODEL = "gpt-4o"
SYSTEM_ROLE = {
    "role": "system",
    "content": "당신은 친절하고 분석적인 AI 튜터입니다."
}

openai.api_key = os.getenv("OPENAI_API_KEY")

async def call_gpt(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=GPT_MODEL,
            messages=[SYSTEM_ROLE, {"role": "user", "content": prompt}],
            timeout=20
        )
        if response and response.choices:
            return response.choices[0].message["content"]
        else:
            return "GPT 응답이 비어있습니다."
    except openai.error.OpenAIError as e:
        return f"GPT 호출 중 오류 발생: {str(e)}"
