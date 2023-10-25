from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class Token:
    text_position: Tuple[int, int]
    wordform: int
    lemma: int
    pos_tag: int

    def __eq__(self, __value) -> bool:
        if __value is None:
            return False
        if not isinstance(__value, Token):
            raise TypeError("Compared value must be the same type.")
        return self.wordform == __value.wordform and \
                self.lemma == __value.lemma and \
                self.pos_tag == __value.pos_tag and \
                self.text_position == __value.text_position

    def __str__(self):
        return f"'{self.wordform}' ({self.lemma}, {self.pos_tag}), {self.text_position}"


class LocalTrigram:

    def __init__(self, sentence_id: int, token_1: Optional[Token] = None, token_2: Optional[Token] = None, token_3: Optional[Token] = None):
        self.token_1, self.token_2, self.token_3 = token_1, token_2, token_3
        self.sentence_id = sentence_id

    def move(self):
        self.token_1, self.token_2, self.token_3 = self.token_2, self.token_3, None
