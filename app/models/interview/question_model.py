from pydantic import BaseModel
from typing import List, Optional

class Question(BaseModel):
    id: int
    category: str
    question: str
    model_answer: str
    sub_id: int
    tags: Optional[List[str]] = []