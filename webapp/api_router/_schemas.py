from pydantic import BaseModel
from typing import Optional


class SearchRequest(BaseModel):

    n_gram: str  # request string
    context_size: Optional[int] = 0  # number of buffer sentences from both sides from the target one

    class Config:
        schema_extra = {
            "example": {
                "n_gram": "проверка",
                "context_size": 0
            }
        }


class WidenContext(BaseModel):
    sentence_id: int
    text_id: int
    context_start: int
    context_end: int
    context_size: Optional[int] = 1  # number of buffer sentences from both sides from the target one

    class Config:
        schema_extra = {
            "example": {
                "sentence_id": 3581,
                "text_id": 177,
                "context_start": 2149,
                "context_end": 2259,
                "context_size": 1
            }
        }