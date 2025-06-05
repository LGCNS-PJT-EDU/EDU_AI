from app.clients.chromadb_client import ChromaClient
import os, json, re
from openai import AsyncOpenAI, APIError, RateLimitError, Timeout

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
chroma_client = ChromaClient()

async def evaluate_answer_with_rag(question: str, user_answer: str) -> dict:
    #  ChromaDB에서 유사 문서 검색
    similar_docs = chroma_client.similarity_search(user_answer, k=3)
    context = "\n".join([doc.page_content for doc in similar_docs])

EVALUATION_RAG_PROMPT = """
당신은 AI 면접관입니다. 아래 면접 질문과 사용자의 답변을 평가하고, 부족한 개념을 보강해주세요

[질문]
{question}

[사용자 답변]
{user_answer}

1.다음 네 가지 항목에 대해 각각 피드백에 반영해주세요.
- 논리성: 답변이 명확한 근거와 전개 흐름을 갖추고 있는가?
- 정확성: 답변 내용이 사실과 일치하며 핵심 개념을 제대로 설명하고 있는가?
- 용어 사용: 전문 용어나 기술 용어를 적절하고 정확하게 사용하였는가?
- 간결함: 중복되거나 불필요한 말 없이 핵심을 효과적으로 전달하고 있는가?

2. 다음과 같은 표현이 자주 사용되면 피드백에 반영해주세요.
예: "음...", "어...", "그니까 뭐랄까...", "그 뭐냐면..."

3. 답변의 강점과 개선점을 간단히 총평으로 써주세요.

4. 이 질문에서 다루는 핵심 개념을 요약해 설명해주세요. (한 문단)

5. 사용자가 더 공부하면 좋은 부분을 짧은 문장으로 3개를 추천해주세요.

반드시 아래 JSON 형식으로만 출력해주세요. 그 외 어떤 설명이나 문장도 포함하지 마세요.

출력 예시:
{{
   "comment": "<총평>",
   "concept_summary": "<핵심 개념 요약>",
   "recommend_keywords": ["...", "...", "..."]
}}
"""

async def evaluate_answer_with_rag(question: str, user_answer: str) -> dict:
    prompt = EVALUATION_RAG_PROMPT.format(question=question, user_answer=user_answer)

    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "당신은 AI 면접관입니다."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        raw = response.choices[0].message.content

        # 코드 블록 제거
        cleaned = re.sub(r"```(?:json)?\n(.*?)\n```", r"\1", raw, flags=re.DOTALL).strip()

        return json.loads(cleaned)

    except (APIError, RateLimitError, Timeout) as e:
        raise RuntimeError(f"OpenAI API 호출 실패: {str(e)}")

    except json.JSONDecodeError as e:
        raise ValueError(f"GPT 응답이 JSON이 아닙니다: {e}\n원본 응답:\n{raw}")


