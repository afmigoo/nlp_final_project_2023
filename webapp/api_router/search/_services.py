from fastapi import HTTPException, status
from ._schemas import SearchRequest

async def _find_n_gram(request: SearchRequest):
