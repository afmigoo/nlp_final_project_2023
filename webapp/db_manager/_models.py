from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey)
from ._core import Base


class Lemmas(Base):
    __tablename__ = 'lemmas'
    id = Column(Integer, primary_key=True)
    text = Column(String(100), comment="Text of lemma")


class WordForms(Base):
    __tablename__ = 'word_forms'
    id = Column(Integer, primary_key=True)
    text = Column(String(100), comment="Text of word form")


class POS(Base):
    __tablename__ = 'pos'
    id = Column(Integer, primary_key=True)
    text = Column(String(100), comment="POS name")


class Trigrams(Base):
    __tablename__ = 'trigrams'
    id = Column(Integer, primary_key=True)
    first_lemma_id = Column('first_lemma_id', Integer, ForeignKey(
        "lemmas.id", ondelete="cascade"))
    first_word_form_id = Column('first_word_form_id', Integer, ForeignKey(
        "word_forms.id", ondelete="cascade"))
    first_pos_id = Column('first_pos_id', Integer, ForeignKey(
        "pos.id", ondelete="cascade"))
    first_sentence_id = Column('first_sentence_id', Integer, ForeignKey(
        "sentences.id", ondelete="cascade"))
    first_start_index = Column(Integer, comment="The index of first token's first character within the text")
    first_end_index = Column(Integer, comment="The index of first token's last character within the text")
    second_lemma_id = Column('second_lemma_id', Integer, ForeignKey(
        "lemmas.id", ondelete="cascade"))
    second_word_form_id = Column('second_word_form_id', Integer, ForeignKey(
        "word_forms.id", ondelete="cascade"))
    second_pos_id = Column('second_pos_id', Integer, ForeignKey(
        "pos.id", ondelete="cascade"))
    second_sentence_id = Column('second_sentence_id', Integer, ForeignKey(
        "sentences.id", ondelete="cascade"))
    second_start_index = Column(Integer, comment="The index of second token's first character within the text")
    second_end_index = Column(Integer, comment="The index of second token's last character within the text")
    third_lemma_id = Column('third_lemma_id', Integer, ForeignKey(
        "lemmas.id", ondelete="cascade"))
    third_word_form_id = Column('third_word_form_id', Integer, ForeignKey(
        "word_forms.id", ondelete="cascade"))
    third_pos_id = Column('third_pos_id', Integer, ForeignKey(
        "pos.id", ondelete="cascade"))
    third_sentence_id = Column('third_sentence_id', Integer, ForeignKey(
        "sentences.id", ondelete="cascade"))
    third_start_index = Column(Integer, comment="The index of third token's first character within the text")
    third_end_index = Column(Integer, comment="The index of third token's last character within the text")


class Sentences(Base):
    __tablename__ = 'sentences'
    id = Column(Integer, primary_key=True)
    start_index = Column(Integer, comment="The index of sentence's first character within the text")
    end_index = Column(Integer, comment="The index of sentence's last character within the text")
    text_id = Column('text_id', Integer, ForeignKey(
        "texts.id", ondelete="cascade"))


class Texts(Base):
    __tablename__ = 'texts'
    id = Column(Integer, primary_key=True)
    text = Column(String(4000), comment="Paste text")
    href = Column(String(400), comment="Link to VK post")
