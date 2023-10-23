from typing import List, Any, Dict, Optional
from stanza.models.common.doc import Sentence
import stanza
import re
from fastapi import status, HTTPException

possible_pos_tags = {
    'ADJ',
    'ADP',
    'ADV',
    'AUX',
    'CCONJ',
    'DET',
    'INTJ',
    'NOUN',
    'NUM',
    'PART',
    'PRON',
    'PROPN',
    'SCONJ',
    'VERB'
}


nlp = stanza.Pipeline(lang='ru', processors='tokenize,pos,lemma')


def get_text_sentences(text: str) -> List[Dict[str, Any]]:
    """Tokenize and POS tag text using Stanza.

    Args:
        text (str): text to parse

    Returns:
        List[Sentence]: tokenized and POS tagged stanza sentences
    """
    doc = nlp(text)
    return doc.to_dict()


def is_a_word(word: str) -> bool:
    """
    Returns true if word is not punctuation. Words like "как-то" are recognized as words, not punctuation.
    """
    return word.isalpha() or bool(re.match(r'[a-zA-Zа-яА-Я]+-?[a-zA-Zа-яА-Я]+', word))


def is_exact_form(word: str) -> bool:
    return bool(re.match(r'\"[a-zA-Zа-яА-Я]*-?[a-zA-Zа-яА-Я]*\"', word))


def is_pos_tag(word: str) -> bool:
    return word in possible_pos_tags


def request_to_trigram(request: str) -> Optional[Dict[int, str]]:
    reqirements_for_tokens = {}
    search_parts = request.strip().split()
    if 4 > len(search_parts) > 0:
        for i, part in enumerate(search_parts):
            part = part.split('+')
            if len(part) == 2:
                stanza_instance = get_text_sentences(part[0])[0][0]
                if not is_pos_tag(part[1]) or not is_a_word(part[0]):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail='В случае запроса через плюс первая часть должна быть леммой, а вторая - pos-тегом')
                reqirements_for_tokens[i + 1] = {'lemma': stanza_instance['lemma'], 'pos': part[1]}
            elif len(part) == 1:
                part = part[0]
                if is_pos_tag(part):
                    reqirements_for_tokens[i + 1] = {'pos': part}
                elif is_exact_form(part):
                    reqirements_for_tokens[i + 1] = {'word_form': part.strip("\"")}
                elif is_a_word(part):
                    stanza_instance = get_text_sentences(part)[0][0]
                    reqirements_for_tokens[i + 1] = {'lemma': stanza_instance['lemma']}
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f'Часть запроса под номером {i + 1} не является ни леммой, ни точной формой, ни pos-тегом')
            elif len(part) >= 3:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Слишком много плюсов')
        return reqirements_for_tokens
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Принимаем от 1- до триграмм')
