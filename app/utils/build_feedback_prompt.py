from app.models.feedback.request import FeedbackRequest

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

        [데이터 저장 구조 예시]
        ```json
        {
          "info": {
            "userId": "3k1_s953",
            "date": "2025-05-13",
            "subject": "Vue.js"
          },
          "scores": {
            "chapter1": 0,
            "chapter2": 0,
            "chapter3": 0,
            "chapter4": 0,
            "chapter5": 0,
            "total":    0
          },
          "feedback": {
            "strength": {
              "chapter1": "good feedback for chapter1",
              "chapter2": "good feedback for chapter2",
              "chapter3": "good feedback for chapter3",
              "chapter4": "good feedback for chapter4",
              "chapter5": "good feedback for chapter5"
            },
            "weakness": {
              "chapter1": "bad feedback for chapter1",
              "chapter2": "bad feedback for chapter2",
              "chapter3": "bad feedback for chapter3",
              "chapter4": "bad feedback for chapter4",
              "chapter5": "bad feedback for chapter5"
            },
            "final": "final summary comment"
          }
        }
"""


def build_feedback_prompt(data: FeedbackRequest) -> str:
    if data.pre_score is not None and data.post_score is not None:

        prompt_body = f"""
당신은 교육 심리 기반의 학습 진단 전문가입니다.

아래 조건을 바탕으로 전문적인 진단 보고서를 작성해주세요:

[학습 대상]
"{data.level}" 수준의 학습자가 "{data.subject}" 과목의 "{data.chapter}" 단원을 학습했습니다.  
이에 대한 이해 수준과 성취 정도를 분석해 주세요.


[출력 형식]
1. 성취 수준 요약 (한 문단)
2. 아직 부족한 부분과 그 원인 (구체 예시 포함)
3. 학습자의 이해를 확장할 수 있는 실전 예시/비유
4. 다음 학습 추천 키워드 3가지 (이해를 기반으로)

※ 400자 이내 요약문으로 작성해주세요.
"""
    elif data.pre_text and data.post_text:
        prompt_body = f"""
당신은 교육 심리 기반의 학습 진단 전문가입니다.

[학습자 응답 비교]
- 사전 답변: "{data.pre_text}"
- 사후 답변: "{data.post_text}"
- 과목: {data.subject}, 단원: {data.chapter}

다음 기준으로 분석해주세요:
1. 지식 수준의 확장 (이전 대비 무엇을 알게 되었는지)
2. 개념 오해 또는 불완전한 설명 요소
3. 실제 상황에서의 적용 가능성 (구현 관점)
4. 추천 보완 개념 3가지 (이해 기반 추천)

※ 전체 400자 이내의 평가 요약문으로 작성해주세요.

[출력 포맷]
반드시 순수 JSON 객체 하나만 반환해주세요.
출력은 반드시 JSON 객체 하나이며, key 순서와 구조를 스키마에 정확히 맞춰 주세요.
"```json" 코드블록, 마크다운 기호, 기타 설명 문장은 절대 포함하지 마세요.

[출력 주의사항]
- JSON 외 텍스트, 마크다운, 설명 문구를 절대 포함하지 마세요.
- JSON 내부 키 순서 및 형식은 스키마를 그대로 따라 주세요.

"""
    else:
        raise ValueError("점수 또는 텍스트가 충분하지 않습니다.")

    return prompt_body + JSON_SCHEMA