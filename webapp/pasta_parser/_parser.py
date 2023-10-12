from nltk import tokenize
from typing import List, Tuple, Generator
from dataclasses import dataclass
from pymorphy2 import MorphAnalyzer
import re

@dataclass
class Token:
    text_position: Tuple[int, int]
    wordform: str
    lemma: str
    pos_tag: str

    def __str__(self):
        return f"'{self.wordform}' ({self.lemma}, {self.pos_tag}), {self.text_position}"

def get_text_tokens(text: str) -> Generator[Token, None, None]:
    tokens = tokenize.word_tokenize(text, language="russian")
    morph = MorphAnalyzer()
    token_filter = r'[a-zA-Zа-яА-Я]+-?[a-zA-Zа-яА-Я]+'
    offset = 0
    for raw_token in tokens:
        if not re.match(token_filter, raw_token): continue
        offset = text.find(raw_token, offset)
        parsed = morph.parse(raw_token)[0]
        yield Token(
            text_position=(offset, offset + len(raw_token)),
            wordform=raw_token.lower(),
            lemma=parsed.normal_form.lower(),
            pos_tag=parsed.tag.POS.lower() if parsed.tag.POS else 'x'
        )
        offset += len(raw_token)
