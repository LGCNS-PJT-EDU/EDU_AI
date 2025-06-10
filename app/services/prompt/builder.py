from collections import defaultdict
from datetime import date
from typing import List

from fastapi import HTTPException

from app.clients import db_clients
from app.models.feedback.request import FeedbackRequest, ChapterData
from app.utils.build_feedback_prompt import (
    build_initial_feedback_prompt,
    build_pre_post_comparison_prompt,
    build_post_post_comparison_prompt
)

user_db = db_clients["user"]
feedback_db = db_clients["feedback"]
assessment_db = db_clients["assessment"]


def calculate_chapter_scores(questions: list[dict]) -> dict[int, tuple[int, int]]:

    difficulty_score_map = {
        "low": 1,
        "medium": 3,
        "high": 5
    }

    chapter_scores = defaultdict(lambda: [0, 0])

    for question in questions:
        chapter_num = question["chapterNum"]
        difficulty = question["difficulty"]
        point = difficulty_score_map.get(difficulty, 0)

        chapter_scores[chapter_num][1] += point

        if question["answerTF"]:
            chapter_scores[chapter_num][0] += point

    return {k: tuple(v) for k, v in chapter_scores.items()}


# 전체 프롬프트 구성
def build_full_prompt(base_prompt: str, subject: str, user_id: str, max_score: int = 20) -> str:
    today = date.today().isoformat()

    return f"""
[RAG 기반 유사 학습 정보]

[사용자 피드백 요청]
{base_prompt}

다음 조건에 맞춰 JSON 피드백을 생성하세요.


<출력 조건>
1. 모든 피드백 문장은 **존댓말**로 작성하고, 반드시 **'-습니다'** 형태의 종결어미를 사용하세요.
2. **모든 내용을 한국어로만 출력**하며, 영어 표현이나 혼용 표현은 절대 사용하지 마세요.
3. 문장은 **친절한 조언 형태**로 표현하고, **무조건적인 평가나 딱딱한 표현**은 지양하세요.
4. **챕터별 피드백은 서로 다른 표현**을 사용하여, 반복되는 문장을 피하세요.
5. **점수가 높은 챕터**는 칭찬 중심으로, **점수가 낮은 챕터**는 구체적인 개선 방향을 1~2문장으로 제시하세요.
6. 최종 코멘트(`final`)는 학습 방향에 대한 **간단한 요약 조언** 과 **전후의 전체적인 총괄적인 피드백** 을 1~2문장으로 구성하세요.
7. **유효한 JSON 형태만 반환**하세요. 마크다운, 인삿말, 코드블록(```) 등은 절대 포함하지 마세요.
8.모든 피드백 문장은 존댓말로 작성하고, 반드시 '-습니다' 형태의 종결어미를 사용하세요. 
9. 모든 내용은 한국어로 작성하며, 영어 표현이나 혼용 표현은 절대 사용하지 마세요. 
10. 피드백은 학습자에게 친절하게 조언하는 어조로 작성하며, 과도하게 단조롭거나 기계적인 표현은 피해주세요. 
11. 아래 JSON 스키마에 따라 순수 JSON 객체 **하나만** 반환하세요. 
12. 인삿말, 설명, 마크다운, 코드블록(```) 등은 절대 포함하지 마세요. 
13. JSON 구조는 유효한 형태여야 하며, 문법 오류(따옴표, 쉼표 등)가 없도록 하세요.

<추론 흐름>
- 결과 도출을 위해 {base_prompt}의 데이터를 사용합니다.
- 먼저 점수(`scores`)를 확인한 뒤, 점수가 높은 챕터부터 강점을 간결하게 정리하세요.
- 이어서 점수가 낮은 챕터를 찾아 개선 방향을 제시하세요.
- 마지막으로, 전체 학습 상황을 요약한 한 문장 이상의 `final` 코멘트를 작성하세요.


<출력 조건>
base_prompt에서 지정한 출력 조건을 아래의 형태로 바꿉니다.

{{
  "info": {{
    "userId": "{user_id}",
    "date": "{today}",
    "subject": "{subject}"
  }},
  "scores": {{
    "CHAPTER_1의 이름": CHAPTER_1의 점수,
    "CHAPTER_2의 이름": CHAPTER_2의 점수,
    "CHAPTER_3의 이름": CHAPTER_3의 점수,
    "CHAPTER_4의 이름": CHAPTER_4의 점수,
    "CHAPTER_5의 이름": CHAPTER_5의 점수,
    "total": {max_score}
  }},
  "feedback": {{
    "strength": {{
      "CHAPTER_1의 이름": CHAPTER_1의 강점,
      "CHAPTER_2의 이름": CHAPTER_2의 강점,
      "CHAPTER_3의 이름": CHAPTER_3의 강점,
      "CHAPTER_4의 이름": CHAPTER_4의 강점,
      "CHAPTER_5의 이름": CHAPTER_5의 강점,
    }},
    "weakness": {{
      "CHAPTER_1의 이름": CHAPTER_1의 약점,
      "CHAPTER_2의 이름": CHAPTER_2의 약점,
      "CHAPTER_3의 이름": CHAPTER_3의 약점,
      "CHAPTER_4의 이름": CHAPTER_4의 약점,
      "CHAPTER_5의 이름": CHAPTER_5의 약점,
    }},
    "final": 종합 평가
  }}
}}
""".strip()


# 상황별 프롬프트 생성
def build_chapter_data(chapters: List[dict], questions: List[dict], max_score) -> List[ChapterData]:
    chapter_score = calculate_chapter_scores(questions)

    chapters_list: list[ChapterData] = []
    for chapter in chapters:
        chapter_num = chapter["chapterNum"]
        score, total_score = chapter_score.get(chapter_num, (0, 0))

        chapter_obj = ChapterData(
            chapterNum=chapter_num,
            chapterName=chapter["chapterName"],
            weakness=chapter["weakness"],
            score=score,
            totalScore=max_score
        )
        chapters_list.append(chapter_obj)

    return chapters_list


def get_max_score_by_level(level):
    if level == "novice":
        return 25
    elif level == "amateur":
        return 35
    elif level == "intermediate":
        return 45
    elif level == "expert":
        return 65
    elif level == "master":
        return 75
    else:
        return HTTPException(status_code=404, detail="Level out of range")


async def generate_feedback_prompt(user_id, subject, subject_id, feedback_type, nth) -> tuple[str, int]:
    user = await user_db.user_profile.find_one({"user_id": user_id})
    user_level = user.get("level", {}).get(str(subject_id))

    try:
        if feedback_type == "PRE":
            pre_assessment_result = await assessment_db.pre_result.find_one(
                {"userId": user_id, "pre_assessment.subject.subjectId": subject_id}
            )
            chapters = pre_assessment_result.get("pre_assessment", {}).get("chapters", [])
            questions = pre_assessment_result.get("pre_assessment", {}).get("questions", [])

            max_score = 20
            chapter_data = build_chapter_data(chapters, questions, max_score)

            pre_feedback_request = FeedbackRequest(
                user_id=str(user_id),
                subject=subject,
                chapter=chapter_data
            )

            base_prompt = build_initial_feedback_prompt(pre_feedback_request)

        elif feedback_type == "POST" and nth == 1:
            pre_feedback = await feedback_db.feedback.find_one({"info.userId": str(user_id), "info.subject": subject}, sort=[("_id", -1)])
            pre_assessment_result = await assessment_db.pre_result.find_one(
                {"userId": user_id, "pre_assessment.subject.subjectId": subject_id})
            post_assessment_result = await assessment_db.post_result.find_one({"userId": user_id})

            post_data = next(
                (v for k, v in post_assessment_result.items()
                 if k.startswith("post_assessments_") and
                 isinstance(v, dict) and
                 v.get("subject", {}).get("subjectId") == subject_id),
                None
            )
            if not post_data:
                raise HTTPException(status_code=404, detail="해당 과목의 사후 평가가 존재하지 않습니다.")

            pre_chapters = pre_assessment_result.get("pre_assessment", {}).get("chapters", [])
            pre_questions = pre_assessment_result.get("pre_assessment", {}).get("questions", [])
            post_chapters = post_data.get("chapters", [])
            post_questions = post_data.get("questions", [])

            max_score = get_max_score_by_level(user_level)
            pre_data = build_chapter_data(pre_chapters, pre_questions, max_score)
            post_data = build_chapter_data(post_chapters, post_questions, max_score)

            pre_request = FeedbackRequest(
                user_id=str(user_id),
                subject=subject,
                chapter=pre_data
            )
            post_request = FeedbackRequest(
                user_id=str(user_id),
                subject=subject,
                chapter=post_data
            )

            base_prompt = build_pre_post_comparison_prompt(pre_feedback, pre_request, post_request)

        else:
            all_post_assessments = await assessment_db.post_result.find_one({"userId": user_id})
            if not all_post_assessments:
                raise HTTPException(status_code=404, detail="해당 사용자의 사후 평가 문서를 찾을 수 없습니다.")

            post_assessments = []
            for k, v in all_post_assessments.items():
                if not k.startswith("post_assessments_"):
                    continue

                try:
                    idx = int(k.split("_")[-1])
                except (ValueError, IndexError):
                    continue

                subject_obj = v.get("subject")
                if isinstance(subject_obj, dict) and subject_obj.get("subjectId") == subject_id:
                    post_assessments.append((idx, v))

            if len(post_assessments) < 2:
                raise HTTPException(status_code=400, detail="해당 과목에 대한 사후 평가가 2회차 이상 존재하지 않습니다.")

            post_assessments.sort(key=lambda x: x[0], reverse=True)
            post_assessment_e = post_assessments[1][1]
            post_assessment_z = post_assessments[0][1]

            prev_feedback = await feedback_db.feedback.find_one({"info.userId": str(user_id), "info.subject": subject}, sort=[("_id", -1)])
            post_score_e = post_assessment_e.get("chapters", [])
            post_score_z = post_assessment_z.get("chapters", [])

            base_prompt = build_post_post_comparison_prompt(prev_feedback, post_score_e, post_score_z)
            max_score = get_max_score_by_level(user_level)


        return base_prompt, max_score

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"피드백 프롬프트 생성 오류: {str(e)}")