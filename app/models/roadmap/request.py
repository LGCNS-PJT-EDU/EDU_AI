# app/models/roadmap/request.py
from pydantic import BaseModel
from typing import Literal, Optional

class RoadmapDetailRequest(BaseModel):
    user_id: str
    track: Literal["frontend", "backend"]
    answers: dict  # { "framework": "Vue", "CI/CD": "Y", ... }
