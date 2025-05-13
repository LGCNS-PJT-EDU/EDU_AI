# app/models/feedback/request.py

from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    user_id: str
    pre_text: str | None = None
    post_text: str | None = None
    pre_score: int | None = None
    post_score: int | None = None
    subject: str
    chapter: str
# 단원명 (예: "JS", "React", "전체")