from pydantic import BaseModel

class EvaluationRequest(BaseModel):
    interviewId: int
    interview_content: str
    user_reply: str
