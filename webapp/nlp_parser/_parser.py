from typing import List, Any, Dict
from stanza.models.common.doc import Sentence
import stanza
import re

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


def is_a_word(word: Dict[str, Any]) -> bool:
    """
    Returns true if word is not punctuation. Words like "как-то" are recognized as words, not punctuation.
    """
    return word['upos'] != 'PUNCT' and (
            word['text'].isalpha()
            or bool(re.match(r'[a-zA-Zа-яА-Я]+-?[a-zA-Zа-яА-Я]+', word['text'])))


def request_to_trigram(request: str):
    