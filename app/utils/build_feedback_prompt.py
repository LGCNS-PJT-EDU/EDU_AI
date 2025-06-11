from typing import Dict, List
from app.models.feedback.request import FeedbackRequest, ChapterData

#  출력 스키마: GPT 출력 포맷 가이드로 사용
BASE_PROMPT = """
{
  "info": {
    "userId": "{user_id}",
    "date": "{today}",
    "subject": "{subject}"
  },
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
    },
    "final": <str>
  }
}
""".strip()


def format_chapters(chapters: List[ChapterData]) -> str:
    return "\n".join(
        f"[{c.chapterNum}] {c.chapterName} - 점수: {c.score}/{c.totalScore}, 약점: {'O' if c.weakness else 'X'}"
        for c in chapters
    )


#  사전 평가 기반 분석용
def build_initial_feedback_prompt(data: FeedbackRequest) -> str:
    return f"""
[사전 평가 분석]
- userId: {data.user_id}
- Subject: {data.subject}
- Chapter 별 정보:
{format_chapters(data.chapter)}

학습자의 현재 이해도를 분석하고,
강점 5가지와 개선이 필요한 약점 5가지를 제시해주세요.

[출력 형식]
{BASE_PROMPT}
""".strip()

#  사전-사후 비교용 프롬프트
def build_pre_post_comparison_prompt(pre_feedback: dict, pre_data: FeedbackRequest, curr_data: FeedbackRequest):
    return f"""
[첫 번째 사후 평가 분석]
- userId: {pre_data.user_id}
- Subject: {pre_data.subject}
- 사전 평가 Chapter 별 정보:
{format_chapters(pre_data.chapter)}
- 사후 평가 Chapter 별 정보:
{format_chapters(curr_data.chapter)}

사전 평가 결과와 사후 평가 결과를 비교분석합니다.
학습자의 현재 이해도를 분석하고,
강점 5가지와 개선이 필요한 약점 5가지를 제시해주세요.

고려할 이전 피드백 최종 요약: "{pre_feedback.get('feedback', {}).get('final', '없음')}"

[출력 형식]
{BASE_PROMPT}
""".strip()

#  사후-사후 반복 비교용
def build_post_post_comparison_prompt(prev_feedback: dict, pre_data: FeedbackRequest, post_data: FeedbackRequest):
    return f"""
[추가 사후 평가 분석]
- userId: {pre_data.user_id}
- Subject: {pre_data.subject}
- 이전 사우 평가 Chapter 별 정보:
{format_chapters(pre_data.chapter)}
- 이번 사후 평가 Chapter 별 정보:
{format_chapters(post_data.chapter)}

사전 평가 결과와 사후 평가 결과를 비교분석합니다.
학습자의 현재 이해도를 분석하고,
강점 5가지와 개선이 필요한 약점 5가지를 제시해주세요.

고려할 이전 피드백 최종 요약: "{prev_feedback.get('feedback', {}).get('final', '없음')}"

[출력 형식]
{BASE_PROMPT}
""".strip()