from typing import List

from pydantic import BaseModel


class ChapterData(BaseModel):
    chapterNum: int
    chapterName: str
    weakness: bool
    cnt: int
    totalCnt: int


class FeedbackRequest(BaseModel):
    user_id: str
    pre_score: int | None = None
    post_score: int | None = None
    pre_text: str | None = None
    post_text: str | None = None
    subject: str = "frontend"
    chapter: List[ChapterData]