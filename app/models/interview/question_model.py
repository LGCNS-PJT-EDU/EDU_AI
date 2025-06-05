from pydantic import BaseModel

class InterviewQuestion(BaseModel):
    interview_content: str
    interview_answer: str
    sub_id: int

