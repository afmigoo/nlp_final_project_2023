from fastapi import HTTPException, status
from ._schemas import SearchRequest
from nlp_parser import request_to_trigram
from db_manager import find_item_id, find_trigram


translate_num = {
    1: 'first',
    2: 'second',
    3: 'third'
}


async def _find_n_gram(request: SearchRequest):
    translated_request = request_to_trigram(request.n_gram)
    request_with_ids = {}
    if translated_request:
        for token_pos, filters in translated_request.items():
            for filter_type, filter_val in filters.items():
                request_with_ids[f'{translate_num[token_pos]}_{filter_type}_id'] = find_item_id(item_type=filter_type,item_val=filter_val)
        # find_trigram(request_with_ids)
        return request_with_ids
    raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Некорректный запрос')