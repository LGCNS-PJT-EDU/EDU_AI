from pydantic import BaseModel, Field
from sqlalchemy import BIGINT


class PreQuestion(BaseModel):
    questionId: int = Field(..., alias="question_id")
    question: str
    choice1: str = Field(..., alias="option1")
    choice2: str = Field(..., alias="option2")
    choice3: str = Field(..., alias="option3")
    choice4: str = Field(..., alias="option4")
    answerNum: int = Field(..., alias="answerIndex")
    chapterNum: int = Field(..., alias="chapterNum")
    chapterName: str = Field(..., alias="chapterName")
    difficulty: str

    class Config:
        allow_population_by_alias = True
        validate_default = True
        extra = "forbid"
        str_strip_whitespace = True