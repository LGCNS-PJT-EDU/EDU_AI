from pydantic import BaseModel


class UserPreference(BaseModel):
    level: str
    duration: int
    price: int
    is_prefer_book: bool