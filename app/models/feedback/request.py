from typing import List

from pydantic import BaseModel


class ChapterData(BaseModel):
    chapterNum: int
    chapterName: str
    weakness: bool
    score: int
    totalScore: int


class FeedbackData(BaseModel):
    chapterName: str
    feedback_text: str


class FeedbackRequest(BaseModel):
    user_id: str
    subject: str
    chapter: List[ChapterData]
    feedback: List[FeedbackData] | None = None