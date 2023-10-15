from typing import List, Tuple, Generator
from stanza.models.common.doc import Sentence, Word
import stanza
import pandas as pd
import re

from ._data_structures import Token, Trigram

nlp = stanza.Pipeline(lang='ru', processors='tokenize,pos,lemma')

def from_csv(csv_path: str) -> List[Tuple[str, str]]:
    """Read csv file and return list of tuples with data where tuple[0] is a text and tuple[1] is a href to a text.

    Args:
        csv_path (str): path to a file

    Returns:
        List[Tuple[str, str]]: Tuple[0] is text, Tuple[1] is href
    """
    df = pd.read_csv(csv_path)
    return [(row.text, row.href) for row in df.itertuples()]

def get_text_sentences(text: str) -> List[Sentence]:
    """Tokenize and POS tag text using Stanza.

    Args:
        text (str): text to parse

    Returns:
        List[Sentence]: tokenized and POS tagged stanza sentences
    """
    doc = nlp(text)
    return doc.sentences

def is_a_word(word: Word) -> bool:
    """
    Returns true if word is not punctuation. Words like "как-то" are recognized as words, not punctuation.
    """
    return bool(re.match(r'[a-zA-Zа-яА-Я]+-?[a-zA-Zа-яА-Я]+', word.text))

def stanza_word_to_token(word: Word, offset: int) -> Token:
    """Helper convertor function. Converts Stanza's Word into ours Token.

    Args:
        word (Word): Stanza's Word obj
        offset (int): word's offset in reference text

    Returns:
        Token: Token obj
    """
    return Token(
        text_position=(offset, offset + len(word.text)),
        wordform=word.text.lower(),
        lemma=word.lemma.lower(),
        pos_tag=word.pos.lower(),
    )

def get_text_trigrams(text: str) -> Generator[Trigram, None, None]:
    """Yields all text's trigrams. 

    Args:
        text (str): Text to parse

    Yields:
        Trigram: Trigram object
    """
    # position of the current token in the reference text
    text_offset = 0
    for sent in get_text_sentences(text):
        # sliding window that remembers last 3 tokens
        current_trigram: List[Token] = [None, None, None]
        trigram_idx = 0
        words = [ w for w in sent.words if is_a_word(w) ]
        if len(words) == 0: continue
        for word in words + [None, None]:
            if word:
                text_offset = text.find(word.text, text_offset)
                token = stanza_word_to_token(word, text_offset)
                text_offset += len(word.text)
            else:
                token = None
            
            current_trigram[trigram_idx%3] = token
            trigram_idx += 1

            yield Trigram(
                tuple(current_trigram[i%3] for i in range(trigram_idx, trigram_idx + 3))
            )
