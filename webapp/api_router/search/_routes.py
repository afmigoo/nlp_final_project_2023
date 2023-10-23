from fastapi import APIRouter, status
from ._services import _find_n_gram
from ._schemas import SearchRequest


router = APIRouter(
    prefix = "/search",
    tags = ["Fuzzy search"])


@router.post(
    path = "/find",
    status_code = status.HTTP_200_OK)
async def find_n_gram(
    request: SearchRequest
):

    response = await _find_n_gram(
        request=request)

    return response