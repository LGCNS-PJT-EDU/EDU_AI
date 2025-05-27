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

[출력 형식 예시]
1단계
- 제목: HTML 기초
- 설명: HTML 태그와 구조를 이해하고 작성할 수 있도록 학습합니다.
- 추천 이유: 프론트엔드 개발의 시작점으로 HTML 이해가 핵심이기 때문입니다.

2단계
...

3단계
...
"""

def build_strategy_prompt(subjects: list[str], level: str, style: str, available_time: str) -> str:
    return f"""
당신은 학습 전략 코치입니다.

다음 조건의 사용자를 위해 각 과목별 학습 전략을 제안해주세요:
- 학습 수준: {level}
- 선호 스타일: {style}
- 학습 가능 시간: {available_time}
- 학습 과목: {', '.join(subjects)}

[출력 형식 예시]
HTML:
- 전략: 강의 수강 후 즉시 코드 실습 반복
- 이유: 초급자는 반복 실습을 통해 개념을 체득할 수 있기 때문입니다.

CSS:
- 전략: 실제 웹페이지 디자인 따라 만들기
- 이유: 실무 유사 프로젝트를 통해 학습 동기와 실력이 동시에 향상됩니다.
"""
