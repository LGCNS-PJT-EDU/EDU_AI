from app.models.feedback.request import FeedbackRequest


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

[출력 형식]
1. 총평 (2~3줄 요약)
2. 강점 3가지 (단어 + 설명)
3. 개선이 필요한 약점 3가지 (단어 + 설명)

※ 각 항목은 명확한 키워드 + 1줄 요약으로 구성해주세요.
"""


def build_roadmap_prompt(user_profile: dict) -> str:
    track = user_profile.get("track", "프론트엔드")
    level = user_profile.get("level", "초급")
    goal = user_profile.get("goal", "포트폴리오 완성")

    return f"""
당신은 교육 커리큘럼 설계 전문가입니다.

다음 조건을 기반으로 사용자에게 최적의 3단계 학습 로드맵을 구성해주세요:
- 트랙: {track}
- 수준: {level}
- 목표: {goal}

[출력 형식]
1단계
- 제목:
- 설명:
- 추천 이유:

2단계
...

3단계
...

※ 각 단계는 실제 기술 키워드 중심으로 명확하고 구체적인 학습 방향을 제시해주세요.
"""


def build_initial_feedback_prompt(data: FeedbackRequest) -> str:
    return f"""
[사전 평가 분석]
- 점수: {data.pre_score}
- 과목: {data.subject}, 단원: {data.chapter}
- 주요 응답: "{data.pre_text}"

학습자의 현재 이해도를 분석하고,
강점 3가지와 개선이 필요한 약점 5가지를 제시해주세요.

※ 각 항목은 단어 + 설명 형식으로 작성해주세요.
"""


def build_pre_post_comparison_prompt(pre_doc, data: FeedbackRequest) -> str:
    pre_score = pre_doc.get("scores", {}).get("pre", 0)

    return f"""
[사전 vs 사후 평가 비교]
- 사전 점수: {pre_score}, 사후 점수: {data.post_score}
- 과목: {data.subject}, 단원: {data.chapter}

점수 변화와 학습자의 성장 정도를 분석하고,
강점 5가지와 보완할 약점 5가지를 구체적으로 제시해주세요.

※ 항목은 단어 + 간단 설명 형식으로 작성해주세요.
"""


def build_post_post_comparison_prompt(prev_post_doc, data: FeedbackRequest) -> str:
    prev_score = prev_post_doc.get("scores", {}).get("post", 0)

    return f"""
[사후 평가 반복 비교]
- 이전 사후 점수: {prev_score}, 최신 사후 점수: {data.post_score}
- 과목: {data.subject}, 단원: {data.chapter}

이전보다 향상된 강점 5가지와 여전히 부족한 약점 5가지를 제시해주세요.

※ 각 항목은 키워드 + 1줄 설명 형식으로 작성해주세요.
"""
