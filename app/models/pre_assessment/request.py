from typing import List

from pydantic import BaseModel


class SubjectInfo(BaseModel):
    subjectId: int
    startDate: str
    duration: int
    submitCnt: int
    level: int
    cnt: int
    totalCnt: int


class ChapterInfo(BaseModel):
    chapterNum : int
    chapterName: str
    weakness: bool
    cnt: int
    totalCnt: int


class QuestionInfo(BaseModel):
    examId: int
    chapterNum: int
    chapterName: str
    difficulty: str
    answerTF: bool
    userAnswer: int


class AssessmentResult(BaseModel):
    subject: SubjectInfo
    chapters: List[ChapterInfo]
    questions: List[QuestionInfo]