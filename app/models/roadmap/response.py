# app/models/roadmap/response.py
from pydantic import BaseModel

class RoadmapRecommendation(BaseModel):
    roadmap_title: str
    roadmap_summary: str
    recommended_steps: list[str]