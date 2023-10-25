from fastapi import HTTPException, status
from nlp_parser import request_to_trigram
from db_manager import find_item_id, find_trigram, create_session, get_context_borders, find_text
from ._schemas import SearchRequest, WidenContext
from typing import List, Dict, Union, Tuple

translate_num = {
    1: 'first',
    2: 'second',
    3: 'third'
}


async def _find_n_gram(
        request: SearchRequest
) -> List[Dict[str, Union[int, str, List[Union[str, Tuple[int, int]]]]]]:
    translated_request = request_to_trigram(request.n_gram)
    if not translated_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Некорректный запрос')
    
    db_formatted_ngram = {}
    for n, filters in translated_request.items():
        for filter_type, filter_val in filters.items():
            db_formatted_ngram[f'{translate_num[n]}_{filter_type}_id'] = find_item_id(
                item_type=filter_type,
                item_val=filter_val)
    return find_trigram(db_formatted_ngram, request.context_size, translate_num[max(translated_request)])


async def _widen_context(
        request: WidenContext
) -> Dict[str, Union[int, str]]:
    session = create_session()
    context_start, context_end = get_context_borders(
        context_size=request.context_size,
        text_id=request.text_id,
        sent_id=request.sentence_id,
        session=session
    )
    context_start = min(context_start, request.context_start) if context_start != -1 else request.context_start
    context_end = max(context_end, request.context_end)
    full_text = find_text(text_id=request.text_id, session=session)[context_start:context_end]
    session.close()
    return {'context_start': context_start, 'context_end': context_end, 'context': full_text}