from typing import Dict

from pydantic import BaseModel


class RecommendRequest(BaseModel):
    query: str
    user_context: Dict[str, int]  # duration_preference, price_preference, likes_books 등