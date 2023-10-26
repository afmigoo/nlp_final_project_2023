from fastapi import APIRouter, status
from ._services import _find_n_gram, _widen_context
from ._schemas import SearchRequest, WidenContext


router = APIRouter(
    prefix="/api")


@router.post(
    path="/find",
    status_code=status.HTTP_200_OK)
async def find_n_gram(
    request: SearchRequest
):

    response = await _find_n_gram(
        request=request)
    return response


@router.post(
    path="/context",
    status_code=status.HTTP_200_OK)
async def widen_context(
    request: WidenContext
):

    response = await _widen_context(
        request=request)
    return response
