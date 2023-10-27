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
    """Find all n_grams that match the given request

    Args:
        request (SearchRequest)

    Returns:
        List[Dict[str, Union[int, str, List[Union[str, Tuple[int, int]]]]]]: all tokens that match the given request.
        Dict format:
            ```
            {
                'context' (str): context, consisting of x <= context_size sentences
                    + target sentence + x <= context_size sentences
                'href' (List[str]): list of links to original posts in VK that include the target sentence
                'context_start' (int): the index of the first character of the context within the text
                'context_end' (int): the index of the last character of the context within the text
                'absolute_ngram_indexes' (List[Tuple[str, str]]): the list of tuples consisting of first and last character
                    indexes within the text of all ngrams found in the sentence
                'sentence_id' (int): id of target sentence in Db,
                'text_id' (int): id of target text in Db
            }
            ```
    """
    translated_request = request_to_trigram(request.n_gram)
    if not translated_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Некорректный запрос')
    
    db_formatted_ngram = {}
    for n, filters in translated_request.items():
        for filter_type, filter_val in filters.items():
            if isinstance(filter_val, str):
                db_formatted_ngram[f'{translate_num[n]}_{filter_type}_id'] = find_item_id(
                    item_type=filter_type,
                    item_val=filter_val)
            elif isinstance(filter_val, list):
                db_formatted_ngram[f'{translate_num[n]}_{filter_type}_id'] = [
                    find_item_id(
                        item_type=filter_type,
                        item_val=val)
                    for val in filter_val
                ]
    return find_trigram(db_formatted_ngram, request.context_size, translate_num[max(translated_request)])


async def _widen_context(
        request: WidenContext
) -> Dict[str, Union[int, str]]:
    """Widen the given context with buffer sentences from both sides

    Args:
        request (WidenContext)

    Returns:
        Dict[str, Union[int, str]]: info about widened context borders and text. Format:
            ```
            {
                'context_start' (int): the index of the first character of the widened context within the text
                'context_end' (int): the index of the last character of the widened context within the text
                'context' (str): widened context
            }
            ```
    """
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