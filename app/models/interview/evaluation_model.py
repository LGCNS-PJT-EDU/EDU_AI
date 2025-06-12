from pydantic import BaseModel

class EvaluationRequest(BaseModel):
    interviewId: int
    interviewContent: str
    userReply: str
