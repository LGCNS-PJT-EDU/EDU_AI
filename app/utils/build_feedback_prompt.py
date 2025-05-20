# app/utils/gpt_prompt/feedback_prompt.py

from app.models.feedback.request import FeedbackRequest
from typing import Dict

def build_growth_feedback_prompt(pre_text: str, post_text: str) -> str:
    return f"""
당신은 학습 성장 분석가입니다.

다음은 학습자의 사전/사후 평가 응답입니다:
- 사전 답변: "{pre_text}"
- 사후 답변: "{post_text}"

이 두 답변을 비교하여 학습자의 성장을 다음 기준으로 평가해주세요:
1. 지식 깊이 향상 여부
2. 구현 능력의 구체성/적용력
3. 논리적 흐름과 설명력

[출력 형식 예시]
1. 총평 (2~3줄 요약)
2. 강점
- 키워드: 설명
...
3. 약점
- 키워드: 설명
...
"""

def build_initial_feedback_prompt(data: FeedbackRequest) -> str:
    return f"""
[사전 평가 분석]
- 점수: {data.pre_score}
- 과목: {data.subject}, 단원: {data.chapter}
- 주요 응답: "{data.pre_text}"

학습자의 현재 이해도를 분석하고,
강점 3가지와 개선이 필요한 약점 5가지를 제시해주세요.

[출력 형식 예시]
- 키워드: 설명
...
"""

def build_pre_post_comparison_prompt(pre_doc: Dict, data: FeedbackRequest) -> str:
    pre_score = pre_doc.get("scores", {}).get("pre", 0)
    return f"""
[사전 vs 사후 평가 비교]
- 사전 점수: {pre_score}, 사후 점수: {data.post_score}
- 과목: {data.subject}, 단원: {data.chapter}

점수 변화와 학습자의 성장 정도를 분석하고,
강점 5가지와 보완할 약점 5가지를 구체적으로 제시해주세요.

[출력 형식 예시]
- 키워드: 설명
...
"""

def build_post_post_comparison_prompt(prev_post_doc: Dict, data: FeedbackRequest) -> str:
    prev_score = prev_post_doc.get("scores", {}).get("post", 0)
    return f"""
[사후 평가 반복 비교]
- 이전 사후 점수: {prev_score}, 최신 사후 점수: {data.post_score}
- 과목: {data.subject}, 단원: {data.chapter}

이전보다 향상된 강점 5가지와 여전히 부족한 약점 5가지를 제시해주세요.

[출력 형식 예시]
- 키워드: 설명
...
"""

JSON_SCHEMA = """
[출력 포맷]
반드시 순수 JSON 객체 하나만 반환해주세요. 다른 설명, 코드블록, 마크다운 문법은 절대 포함하지 마세요.

스키마:
{
  "info": {
    "userId": "<string>",
    "date": "<YYYY-MM-DD>",
    "subject": "<string>"
  },
  "scores": {
    "chapter1": <int>,
    "chapter2": <int>,
    "chapter3": <int>,
    "chapter4": <int>,
    "chapter5": <int>,
    "total":    <int>
  },
  "feedback": {
    "strength": { "<key>": "<문장>", ... },
    "weakness": { "<key>": "<문장>", ... },
    "final":     "<최종 코멘트>"
  }
}
"""

def build_feedback_prompt(data: FeedbackRequest) -> str:
    if data.pre_score is not None and data.post_score is not None:
        prompt_body = f"""
당신은 교육 심리 기반의 학습 진단 전문가입니다.

[학습 데이터]
- 과목: {data.subject}
- 단원: {data.chapter}

1. 성취 수준 요약
2. 부족한 부분 원인
3. 실전 예시/비유
4. 추천 키워드 3가지

※ 400자 이내 요약문으로 작성해주세요.
"""
    elif data.pre_text and data.post_text:
        prompt_body = f"""
당신은 교육 심리 기반의 학습 진단 전문가입니다.

[학습자 응답 비교]
- 사전 답변: "{data.pre_text}"
- 사후 답변: "{data.post_text}"
- 과목: {data.subject}, 단원: {data.chapter}

1. 지식 수준의 확장 (이전 대비 무엇을 알게 되었는지)
2. 개념 오해 또는 불완전한 설명 요소
3. 실제 상황에서의 적용 가능성 (구현 관점)
4. 추천 보완 개념 3가지 (이해 기반 추천) 

※ JSON으로 작성해주세요.
"""
    else:
        raise ValueError("점수 또는 텍스트가 충분하지 않습니다.")

    return prompt_body + JSON_SCHEMA