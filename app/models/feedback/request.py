from pydantic import BaseModel


class FeedbackRequest(BaseModel):
    user_id: str
    pre_text: str
    post_text: str