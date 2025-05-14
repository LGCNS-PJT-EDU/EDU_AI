from app.models.feedback.request import FeedbackRequest


def build_feedback_prompt(data: FeedbackRequest) -> str:
    if data.pre_score is not None and data.post_score is not None:
        gap = data.post_score - data.pre_score
        summary = f"사전 평가 점수: {data.pre_score}, 사후 평가 점수: {data.post_score} → 변화: {gap:+}점"

        return f"""
당신은 교육 심리 기반의 학습 진단 전문가입니다.

아래 조건을 바탕으로 전문적인 진단 보고서를 작성해주세요:

[학습 데이터]
- 과목: {data.subject}
- 단원: {data.chapter}
- {summary}

[출력 형식]
1. 성취 수준 요약 (한 문단)
2. 아직 부족한 부분과 그 원인 (구체 예시 포함)
3. 학습자의 이해를 확장할 수 있는 실전 예시/비유
4. 다음 학습 추천 키워드 3가지 (이해를 기반으로)

※ 400자 이내 요약문으로 작성해주세요.
"""
    elif data.pre_text and data.post_text:
        return f"""
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
"""
    else:
        raise ValueError("점수 또는 텍스트가 충분하지 않습니다.")