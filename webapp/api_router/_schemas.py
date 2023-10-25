from pydantic import BaseModel


class SearchRequest(BaseModel):

    n_gram: str
    context_size: int | None = 0

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
    context_size: int | None = 1

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