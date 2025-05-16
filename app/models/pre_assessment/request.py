from typing import List

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