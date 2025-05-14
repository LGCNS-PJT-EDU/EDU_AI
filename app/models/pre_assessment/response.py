from pydantic import BaseModel, Field


class PreQuestion(BaseModel):
    question_id: int
    question: str
    choice1: str = Field(..., alias="option1")
    choice2: str = Field(..., alias="option2")
    choice3: str = Field(..., alias="option3")
    choice4: str = Field(..., alias="option4")
    answer_num: int = Field(..., alias="answerIndex")
    chapter_num: int = Field(..., alias="chapterNum")
    chapter_name: str = Field(..., alias="chapterName")
    difficulty: str

    class Config:
        allow_population_by_alias = True
        by_alias = False
        validate_all = True
        extra = "forbid"
        anystr_strip_whitespace = True