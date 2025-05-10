from typing import Dict
from pydantic import BaseModel, Field
from datetime import date


class FeedbackInput(BaseModel):
    user_id: str
    pre_text: str
    post_text: str

class Feedback(BaseModel):
    strength: Dict[str, str]
    weakness: Dict[str, str]
    final: str

    model_config = {
        "populate_by_name": True,
        "populate_by_alias": True
    }

class Info(BaseModel):
    user_id: str  = Field(..., alias="userId")
    date:    date
    subject: str

    model_config = {
        "populate_by_name":  True,
        "populate_by_alias": True
    }

class FeedbackResponse(BaseModel):
    info: Info
    scores: Dict[str, int]
    feedback: Feedback

    model_config = {
        "populate_by_name":  True,
        "populate_by_alias": True
    }
