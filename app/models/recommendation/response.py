from pydantic import BaseModel


class RecommendResponse(BaseModel):
    title: str
    url: str
    type: str
    platform: str
    duration: str
    level: str
    price: str
    ai_pick: bool = False