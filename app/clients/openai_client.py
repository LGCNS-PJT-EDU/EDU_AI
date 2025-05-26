import os

import openai
from dotenv import load_dotenv


load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class OpenAiClient:
    def __init__(self, model="gpt-4o", temperature=0.7, max_tokens=800):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def create_chat_response(self, system_prompt: str, user_prompt: str) -> str:
        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

        return response.choices[0].message.content