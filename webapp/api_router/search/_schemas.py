from pydantic import BaseModel


class SearchRequest(BaseModel):

    n_gram: str

    class Config:
        schema_extra = {
            "example": {
                "n_gram": "проверка",

            }
        }