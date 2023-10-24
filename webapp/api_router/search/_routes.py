from fastapi import APIRouter, status
from ._services import _find_n_gram


router = APIRouter(
    prefix = "/search",
    tags = ["Fuzzy search"])


@router.get(
    path = "/find/{request}",
    status_code = status.HTTP_200_OK)
async def find_n_gram(
    request: str,
    context_size: int | None = None
):
    if context_size == None: context_size = 0
    response = await _find_n_gram(
        request=request,
        context_size=context_size)

    return response
