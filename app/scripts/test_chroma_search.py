from app.services.recommendation.rag_explainer import explain_reason_with_rag

title = "생활코딩-HTML"
user_context = "HTML 기초를 배우려는 웹개발 입문자입니다."

result = explain_reason_with_rag(title, user_context)
print(" 추천 이유:\n", result)

