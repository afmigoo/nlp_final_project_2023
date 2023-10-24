from fastapi import HTTPException, status
from nlp_parser import request_to_trigram
from db_manager import find_item_id, find_trigram


translate_num = {
    1: 'first',
    2: 'second',
    3: 'third'
}

async def _find_n_gram(request: str, context_size: int):
    translated_request = request_to_trigram(request)
    if not translated_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Некорректный запрос')
    
    db_formatted_ngram = {}
    for n, filters in translated_request.items():
        for filter_type, filter_val in filters.items():
            db_formatted_ngram[f'{translate_num[n]}_{filter_type}_id'] = find_item_id(item_type=filter_type,item_val=filter_val)
    return find_trigram(db_formatted_ngram, context_size)
