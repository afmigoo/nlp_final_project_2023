from typing import Any, Dict, Union, List, Tuple
from ._models import *
from ._core import SessionLocal
from nlp_parser import get_text_sentences, is_a_word, Token, LocalTrigram
import csv
import os
from tqdm import tqdm
from math import inf
from sqlalchemy import select, and_
from fastapi import status, HTTPException

translate_num = {
    1: 'first',
    2: 'second',
    3: 'third'
}

def create_session() -> Any:
    session = SessionLocal()
    return session


def db_notempty() -> int:
    session = create_session()
    response = len(session.query(Texts).all()) > 0
    session.close()
    return response


def add_class_to_session(session: SessionLocal, item_class: Any) -> int:
    session.add(item_class)
    session.commit()
    return item_class.id


def check_if_exists(session: SessionLocal, existing_dict: Dict[str, Dict[str, int]], item_type: str, stanza_item: str, item_class: Any):
    if stanza_item[item_type] in existing_dict[item_type]:
        return existing_dict[item_type][stanza_item[item_type]]
    item_class.text = stanza_item[item_type]
    item_id = add_class_to_session(session=session, item_class=item_class)
    existing_dict[item_type][stanza_item[item_type]] = item_id
    return item_id

def local_trigram_to_db_class(local_trigram: LocalTrigram) -> Trigrams:
    trigram_copy = LocalTrigram(
        local_trigram.sentence_id,
        local_trigram.token_1,
        local_trigram.token_2,
        local_trigram.token_3,
    )
    if trigram_copy.token_1 == trigram_copy.token_2 == trigram_copy.token_3 == None:
        raise ValueError("All tokens cant be None")
    # moving trigram until all nones are in the end 
    while trigram_copy.token_1 == None:
        trigram_copy.move()
    return Trigrams(
        sentence_id=trigram_copy.sentence_id,
        first_lemma_id = trigram_copy.token_1.lemma,
        first_word_form_id = trigram_copy.token_1.wordform,
        first_pos_id = trigram_copy.token_1.pos_tag,
        first_start_index = trigram_copy.token_1.text_position[0],
        first_end_index = trigram_copy.token_1.text_position[1],
        second_lemma_id = trigram_copy.token_2.lemma if trigram_copy.token_2 else None,
        second_word_form_id = trigram_copy.token_2.wordform if trigram_copy.token_2 else None,
        second_pos_id = trigram_copy.token_2.pos_tag if trigram_copy.token_2 else None,
        second_start_index = trigram_copy.token_2.text_position[0] if trigram_copy.token_2 else None,
        second_end_index = trigram_copy.token_2.text_position[1] if trigram_copy.token_2 else None,
        third_lemma_id = trigram_copy.token_3.lemma if trigram_copy.token_3 else None,
        third_word_form_id = trigram_copy.token_3.wordform if trigram_copy.token_3 else None,
        third_pos_id = trigram_copy.token_3.pos_tag if trigram_copy.token_3 else None,
        third_start_index = trigram_copy.token_3.text_position[0] if trigram_copy.token_3 else None,
        third_end_index = trigram_copy.token_3.text_position[1] if trigram_copy.token_3 else None
    )


def fill_db(path: str = str(os.path.join(os.getcwd(), 'instance', 'corpora_past.csv'))):
    limit = inf
    session = create_session()
    already_added_items = {'lemma': {}, 'text': {}, 'upos': {}}
    with open(path, 'r', encoding='utf-8') as f:
        for text in tqdm(csv.DictReader(f), position=0, desc="Text", unit='t'):
            if limit == 0: break
            limit -= 1
            text_id = add_class_to_session(session=session, item_class=Texts(full_text=text['text'], href=text['href']))
            for sentence_tokens in tqdm(get_text_sentences(text['text']), position=1, desc="Sent", unit='s', leave=False):
                sentence_tokens = [ t for t in sentence_tokens if is_a_word(t['text']) ]
                if len(sentence_tokens) == 0: continue
                sentence_id = add_class_to_session(session=session, item_class=Sentences(
                    start_index=sentence_tokens[0]['start_char'],
                    end_index=sentence_tokens[-1]['end_char'],
                    text_id=text_id))
                current_trigram = LocalTrigram(sentence_id)
                for token in sentence_tokens:
                    token['text'], token['lemma'] = token['text'].lower(), token['lemma'].lower()
                    lemma_id = check_if_exists(
                        session=session,
                        existing_dict=already_added_items,
                        item_type='lemma',
                        stanza_item=token,
                        item_class=Lemmas(),
                    )
                    word_form_id = check_if_exists(
                        session=session,
                        existing_dict=already_added_items,
                        item_type='text',
                        stanza_item=token,
                        item_class=WordForms(),
                    )
                    pos_id = check_if_exists(
                        session=session,
                        existing_dict=already_added_items,
                        item_type='upos',
                        stanza_item=token,
                        item_class=POS(),
                    )
                    current_trigram.move()
                    current_trigram.token_3 = Token(
                        text_position=(token['start_char'], token['end_char']),
                        wordform=word_form_id,
                        lemma=lemma_id,
                        pos_tag=pos_id)
                    add_class_to_session(session=session, item_class=local_trigram_to_db_class((current_trigram)))
                for _ in range(2):
                    current_trigram.move()
                    add_class_to_session(session=session, item_class=local_trigram_to_db_class((current_trigram)))

    session.close()


def find_item_id(item_type: str, item_val: str):
    item_class = Lemmas if item_type == 'lemma' else POS if item_type == 'pos' else WordForms
    session = create_session()
    item_id = session.execute(select(item_class.id).where(item_class.text == item_val)).all()
    session.close()
    if len(item_id):
        return item_id[0][0]
    label = 'леммы' if item_type == 'lemma' else 'POS-тега' if item_type == 'pos' else 'словоформы'
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'В корпусе нет {label} {item_val}')

def get_context_borders(context_size: int, text_id: int, sent_id: int, session) -> Tuple[int, int]:
    """Узнать границы контекста в рамках оригинального текста.

    Args:
        context_size (int): сколько предложений слева и справа в контексте
        text_id (int): id оригинального текста
        sent_id (int): id целевого предложения
        session (_type_): лень шарить какой тип. Сессия которая create_session()

    Returns:
        Tuple[int, int]: Границы контекста в оригинальном тексте. 
        Возвращает (-1, -1) если размер контекста = 0 (т.е. расширять его не надо) или 
        если в теории предложение единственное в тексте.
    """
    if context_size == 0: return (-1, -1)
    query = select(
        Texts.full_text,
        Sentences.id.label('sent_id'), Sentences.start_index, Sentences.end_index
    ) \
    .join(Sentences, Sentences.text_id == Texts.id) \
    .where(
        and_(
            Texts.id == text_id,
            Sentences.id <= sent_id + context_size,
            Sentences.id >= sent_id - context_size,
            Sentences.id != sent_id,
        )
    )
    raw_contexts = session.execute(query)
    min_idx = inf; max_idx = -1
    for row in raw_contexts:
        if row.start_index < min_idx: min_idx = row.start_index
        if row.end_index > max_idx: max_idx = row.end_index
    return (-1 if min_idx == inf else min_idx, max_idx)

def find_trigram(clauses: Dict[str, int], context_size: int = 1) -> List[Dict[str, Union[int, str]]]:
    """Найти подходящие по условиям триграммы и выдать их в контексте.

    Args:
        clauses (Dict[str, int]): условия для триграм. Напр: {"first_lemma_id": 127, "second_pos_id": 4}
        context_size (int, optional): Размер контекста (колво предложений слева и справа). Defaults to 1.

    Returns:
        List[Dict[str, Union[int, str]]]: list of dicts. Dict format:
        
        ```
        {
            'context': str, # Контекст, текст. `context_size` предложений + предложение с найденной нграмой + `context_size` предложений
            'href': str, # Ссылка на оригинальный пост во Вконтакте
            'trigram': str, # Текст нграмы
            'trigram_context_start': int, # Индекс где в данном контексте начинается нграма
            'trigram_context_end': int, # Индекс где в данном контексте закончивается нграма
        }
        ```
    """
    ngram_len = -1
    trigrams = select(
        Texts.id.label('text_id'), Texts.full_text, Texts.href,
        Sentences.id.label('sent_id'), Sentences.start_index, Sentences.end_index,
        Trigrams.first_start_index, Trigrams.first_end_index,
        Trigrams.second_start_index, Trigrams.second_end_index,
        Trigrams.third_start_index, Trigrams.third_end_index,
    ) \
    .join(Trigrams, Trigrams.sentence_id == Sentences.id) \
    .join(Texts, Texts.id == Sentences.text_id)
    for key, item_id in clauses.items():
        trigrams = trigrams.where(getattr(Trigrams, key) == item_id)
        # определяем длину нграммы
        for num, str_num in translate_num.items():
            if str_num in key and ngram_len < num: 
                ngram_len = num
                break

    session = create_session()
    output = session.execute(trigrams).all()
    
    last_gram_key = translate_num[ngram_len] + '_end_index'
    result = []
    for row in output:
        context_start, context_end = get_context_borders(context_size, row.text_id, row.sent_id, session)
        context_start = row.start_index if context_start == -1 else context_start
        context_end = row.end_index if context_end == -1 else context_end
        result.append({
            'context': row.full_text[context_start:context_end],
            'href': row.href,
            'trigram': row.full_text[row.first_start_index:getattr(row, last_gram_key)],
            'trigram_context_start': row.first_start_index - context_start,
            'trigram_context_end': getattr(row, last_gram_key) - context_start,
        })

    session.close()
    return result
