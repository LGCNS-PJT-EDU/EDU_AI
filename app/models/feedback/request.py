# app/models/feedback/request.py

from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    user_id: str
    pre_score: int | None = None
    post_score: int | None = None
    pre_text: str | None = None
    post_text: str | None = None
    subject: str = "frontend"
    chapter: str = "전체"  # 단원명 (예: "JS", "React", "전체")
