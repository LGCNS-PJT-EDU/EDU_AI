from pydantic import BaseModel, Field


class RecommendationResponse(BaseModel):
    contentId: int
    subjectId: int
    title: str
    url: str
    type: str
    platform: str
    duration: str
    price: str
    is_ai_recommendation: bool = Field(False, alias="isAiRecommendation")

    class Config:
        allow_population_by_alias = True