from fastapi import APIRouter
from pydantic import BaseModel
from typing import Union, List

#from db_manager import DataBase

class Token(BaseModel):
    wordform: Union[str, None]
    lemma: Union[str, None]
    pos: Union[str, None]

class Ngram(BaseModel):
    ngrams: List[Union[Token, None]]

search = APIRouter(prefix='/search', tags=['search'])
data = APIRouter(prefix='/data', tags=['texts'])

@search.get('/ngram')
async def search_ngram(ngram: Ngram):
    return {"message": f"Ngram search. Your ngram: {ngram}"}

@data.get('/pasta/{pasta_id}')
async def get_pasta(pasta_id: int):
    return {"message": f"You requested pasta with id={pasta_id}"}