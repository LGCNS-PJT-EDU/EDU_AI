from pydantic import BaseModel


class UserPreference(BaseModel):
    level: str
    duration: str
    price: str
    is_prefer_book: bool