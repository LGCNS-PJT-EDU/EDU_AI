from datetime import date
from typing import List, Dict

from pydantic import BaseModel


class AnswerItem(BaseModel):
    question_id: str
    correct: bool
    difficulty: str


class PretestSubmitInput(BaseModel):
    user_id: str
    answers: List[AnswerItem]


class AssessmentInput(BaseModel):
    survey_answers: dict
    pre_test_score: int


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