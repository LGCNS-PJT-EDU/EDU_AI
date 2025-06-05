from pydantic import BaseModel

class EvaluationRequest(BaseModel):
    question: str
    user_answer: str
