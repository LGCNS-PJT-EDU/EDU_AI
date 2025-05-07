def build_growth_feedback_prompt(pre_text, post_text):
    return f"""
사전 답변: "{pre_text}"

사후 답변: "{post_text}"

두 답변을 비교해 사용자 성장 정도를 다음 3가지 측면에서 분석해 주세요:
- 지식 깊이
- 구현 능력
- 논리적 표현력

분석 결과를 다음과 같이 작성해주세요:

1. 총평 (3줄 이내 요약)
2. 성장 포인트 3가지
3. 개선할 점 3가지
"""


