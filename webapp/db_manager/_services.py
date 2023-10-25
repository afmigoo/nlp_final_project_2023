from typing import Any, Dict, Union, List, Tuple
from ._models import *
from ._core import SessionLocal, vk_access_token, vk_page, vk_version
from nlp_parser import get_text_sentences, is_a_word, Token, LocalTrigram
import os
from tqdm import tqdm
from math import inf
from sqlalchemy import select, and_
from fastapi import status, HTTPException
import json
import requests


def create_session() -> SessionLocal:
    session = SessionLocal()
    return session


def db_notempty() -> bool:
    session = create_session()
    response = len(session.query(Texts).all()) > 0
    session.close()
    return response


def add_class_to_session(
        session: SessionLocal,
        item_class: Any,
        need_commit: bool = True
) -> int:
    session.add(item_class)
    if need_commit:
        session.commit()
    return item_class.id


def check_if_exists(
        session: SessionLocal,
        existing_dict: Dict[str, Dict[str, int]],
        item_type: str,
        stanza_item: str,
        item_class: Any
) -> int:
    if stanza_item[item_type] in existing_dict[item_type]:
        return existing_dict[item_type][stanza_item[item_type]]
    item_class.text = stanza_item[item_type]
    item_id = add_class_to_session(session=session, item_class=item_class)
    existing_dict[item_type][stanza_item[item_type]] = item_id
    return item_id


def parse_from_vk_api(
        result_path: str = str(os.path.join(os.getcwd(), 'instance', 'corpora_past.json'))
) -> None:
    pasty = []
    pasty_unique = set()
    print('Краулим пасты с помощью vk api')
    for offset in tqdm(range(0, 3000, 100)):
        response = requests.get('https://api.vk.com/method/wall.get',
        params={'access_token': vk_access_token,
                'v': vk_version,
                'domain': vk_page,
                'count': 100,
                'offset': offset})
        data = response.json()
        for post in data['response']['items']:
            if len(post['text'].split()) > 10 and post['text'] not in pasty_unique:
                pasty_unique.add(post['text'])
                pasty.append({'text': post['text'], 'href': 'https://vk.com/wall' + str(post['from_id']) + '_' + str(post['id'])})
    with open(result_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(pasty, ensure_ascii=False))


def local_trigram_to_db_class(
        local_trigram: LocalTrigram
) -> Trigrams:
    return Trigrams(
        sentence_id=local_trigram.sentence_id,
        first_lemma_id=local_trigram.token_1.lemma,
        first_word_form_id=local_trigram.token_1.wordform,
        first_pos_id=local_trigram.token_1.pos_tag,
        first_start_index=local_trigram.token_1.text_position[0],
        first_end_index=local_trigram.token_1.text_position[1],
        second_lemma_id=local_trigram.token_2.lemma if local_trigram.token_2 else None,
        second_word_form_id=local_trigram.token_2.wordform if local_trigram.token_2 else None,
        second_pos_id=local_trigram.token_2.pos_tag if local_trigram.token_2 else None,
        second_start_index=local_trigram.token_2.text_position[0] if local_trigram.token_2 else None,
        second_end_index=local_trigram.token_2.text_position[1] if local_trigram.token_2 else None,
        third_lemma_id=local_trigram.token_3.lemma if local_trigram.token_3 else None,
        third_word_form_id=local_trigram.token_3.wordform if local_trigram.token_3 else None,
        third_pos_id=local_trigram.token_3.pos_tag if local_trigram.token_3 else None,
        third_start_index=local_trigram.token_3.text_position[0] if local_trigram.token_3 else None,
        third_end_index=local_trigram.token_3.text_position[1] if local_trigram.token_3 else None
    )


def fill_db(
        path: str = str(os.path.join(os.getcwd(), 'instance', 'corpora_past.json'))
) -> None:
    if not os.path.isfile(path):
        parse_from_vk_api(path)
    session = create_session()
    already_added_items = {'lemma': {}, 'text': {}, 'upos': {}}
    print('Пишем в бд')
    with open(path, 'r', encoding='utf-8') as f:
        for text in tqdm(json.loads(f.read())):
            text_id = add_class_to_session(session=session, item_class=Texts(full_text=text['text'], href=text['href']))
            for sentence_tokens in get_text_sentences(text['text']):
                sentence_id = add_class_to_session(session=session, item_class=Sentences(
                    start_index=sentence_tokens[0]['start_char'],
                    end_index=sentence_tokens[-1]['end_char'],
                    text_id=text_id))
                current_trigram = LocalTrigram(sentence_id)
                for token in sentence_tokens:
                    if is_a_word(token['text']):
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
                        if current_trigram.token_1 is not None:
                            add_class_to_session(session=session, item_class=local_trigram_to_db_class(current_trigram), need_commit=False)
                for _ in range(2):
                    current_trigram.move()
                    if current_trigram.token_1 is not None:
                        add_class_to_session(session=session, item_class=local_trigram_to_db_class(current_trigram), need_commit=False)

    session.close()


def find_item_id(
        item_type: str,
        item_val: str
) -> int:
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


def get_context_borders(
        context_size: int,
        text_id: int,
        sent_id: int,
        session: SessionLocal
) -> Tuple[int, int]:
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
    if not context_size:
        return -1, 1
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
    return -1 if min_idx == inf else min_idx, max_idx


def find_text(
        text_id: int,
        session: SessionLocal
) -> str:
    return session.get(Texts, text_id).full_text


def find_trigram(
        clauses: Dict[str, int],
        context_size: int = 0,
        ngram_last_num: str = 'third'
) -> List[Dict[str, Union[int, str, List[Union[str, Tuple[int, int]]]]]]:
    """Найти подходящие по условиям триграммы и выдать их в контексте.

    Args:
        clauses (Dict[str, int]): условия для триграм. Напр: {"first_lemma_id": 127, "second_pos_id": 4}
        context_size (int, optional): Размер контекста (колво предложений слева и справа). Defaults to 1.

    Returns:
        List[Dict[str, Union[int, str]]]: list of dicts. Dict format:
        
        ```
        {
            'context': str, # Контекст, текст. `context_size` предложений + предложение с найденной нграмой
                        + `context_size` предложений
            'href': str, # Ссылка на оригинальный пост во Вконтакте
            'trigram': str, # Текст нграмы
            'trigram_context_start': int, # Индекс где в данном контексте начинается нграма
            'trigram_context_end': int, # Индекс где в данном контексте закончивается нграма
        }
        ```
    """
    last_gram_key = ngram_last_num + '_end_index'

    trigrams = select(
        Texts.id.label('text_id'), Texts.full_text, Texts.href,
        Sentences.id.label('sent_id'), Sentences.start_index, Sentences.end_index,
        Trigrams.first_start_index, getattr(Trigrams, last_gram_key),
    ) \
    .join(Trigrams, Trigrams.sentence_id == Sentences.id) \
    .join(Texts, Texts.id == Sentences.text_id)
    for key, item_id in clauses.items():
        trigrams = trigrams.where(getattr(Trigrams, key) == item_id)

    session = create_session()
    output = session.execute(trigrams).all()

    result = {}
    for row in output:
        context_start, context_end = get_context_borders(context_size, row.text_id, row.sent_id, session)
        context_start = min(row.start_index, context_start) if context_start > -1 else row.start_index
        context_end = max(row.end_index, context_end)
        result_text = row.full_text[context_start:context_end]
        result.setdefault(
            result_text,
            {
                'sentence_id': -1,
                'hrefs': set(),
                'context_start': -1,
                'indexes': set(),
                'context_end': -1,
                'absolute_indexes': set(),
                'text_id': -1
            }
        )
        result[result_text]['hrefs'].add(row.href)
        if (
                (row.first_start_index - context_start, getattr(row, last_gram_key) - context_start)
                not in result[result_text]['indexes']
        ):
            result[result_text]['absolute_indexes'].add((row.first_start_index, getattr(row, last_gram_key)))
        result[result_text]['indexes'].add(
            (row.first_start_index - context_start, getattr(row, last_gram_key) - context_start)
        )
        result[result_text]['sentence_id'] = (
            row.sent_id if result[result_text]['sentence_id'] == -1 else result[result_text]['sentence_id']
        )
        result[result_text]['text_id'] = (
            row.text_id if result[result_text]['text_id'] == -1 else result[result_text]['text_id']
        )
        result[result_text]['context_start'] = (
            context_start if result[result_text]['context_start'] == -1 else result[result_text]['context_start']
        )
        result[result_text]['context_end'] = (
            context_end if result[result_text]['context_end'] == -1 else result[result_text]['context_end']
        )
    result_json = []
    for text, info in result.items():
        result_json.append({
            "context": text,
            "href": list(info['hrefs']),
            "context_start": info['context_start'],
            "context_end": info['context_end'],
            "absolute_ngram_indexes": sorted(list(info['absolute_indexes'])),
            "sentence_id": info['sentence_id'],
            "text_id": info['text_id']
        })
    session.close()
    if not len(result_json):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'По запросу ничего не нашлось :(')
    return result_json
