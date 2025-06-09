from typing import Dict
from app.models.feedback.request import FeedbackRequest

#  출력 스키마: GPT 출력 포맷 가이드로 사용
BASE_PROMPT = """
    BASE_PROMPT = {
      "scores": {
        "{chapter1}": <int>,
        "{chapter2}": <int>,
        "{chapter3}": <int>,
        "{chapter4}": <int>,
        "{chapter5}": <int>,
        "{cnt}":    <int>
      },
      "feedback": {
        "strength": {
            "{chapter1}": <str>,
            "{chapter2}": <str>,
            "{chapter3}": <str>,
            "{chapter4}": <str>,
            "{chapter5}": <str>
        },
        "weakness": {
            "{chapter1}": <str>,
            "{chapter2}": <str>,
            "{chapter3}": <str>,
            "{chapter4}": <str>,
            "{chapter5}": <str>
        }
        "final": <str>
      }
"""

#  기본 사전/사후 텍스트 비교용
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

#  사전 평가 기반 분석용
def build_initial_feedback_prompt(data: FeedbackRequest) -> str:
    return f"""
        [사전 평가 분석]
        - 점수: {data.pre_score}
        - 과목: {data.subject}, 단원: {data.chapter}
        - 주요 응답: "{data.pre_text}"
        
        학습자의 현재 이해도를 분석하고,
        강점 5가지와 개선이 필요한 약점 5가지를 제시해주세요.
        
        [출력 형식 예시]
        {BASE_PROMPT}의 형태로 출력 형태를 만들어 주세요.
    """

#  사전-사후 비교용 프롬프트
def build_pre_post_comparison_prompt(pre_feedback, pre_data, curr_data):
    return f"""
        사전 평가 데이터인 {pre_data}와 첫 번째 사후 평가 데이터인 {curr_data}을 사용해서 피드백을 만들어 주세요.
        단, 사전 평가 기반 피드백인 {pre_feedback}에 기반해서 결과를 만들어야 합니다.
        출력 형태는 {BASE_PROMPT}입니다.
    """

#  사후-사후 반복 비교용
def build_post_post_comparison_prompt(prev_feedback, recent_assessment, most_recent_assessment):
    return f"""
        {recent_assessment}와 {most_recent_assessment}를 비교해서 결과를 출력해주세요.
        단, 최근 피드백인 {prev_feedback}을 고려해야 합니다.
        출력 형태는 {BASE_PROMPT}입니다.
    """