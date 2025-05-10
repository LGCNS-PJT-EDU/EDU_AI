# app/gpt_prompt.py

def build_growth_feedback_prompt(pre_text: str, post_text: str) -> str:
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


def build_roadmap_prompt(user_profile: dict) -> str:
    track = user_profile.get("track", "프론트엔드")
    level = user_profile.get("level", "초급")
    goal = user_profile.get("goal", "포트폴리오 완성")

    return f"""
사용자는 {track}를 희망하고, 수준은 {level}이며 목표는 {goal}입니다.
이에 맞춰 3단계 학습 로드맵을 구성해주세요.

각 단계는 다음 형식을 따르도록 해주세요:
- 제목
- 설명
- 추천 이유
"""


