from typing import Any, Dict
from ._models import *
from ._core import SessionLocal
from nlp_parser import get_text_sentences, is_a_word, Token, LocalTrigram
import csv
import os
from tqdm import tqdm
from sqlalchemy import select
from fastapi import status, HTTPException

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
    return Trigrams(
        first_lemma_id = local_trigram.token_1.lemma,
        first_word_form_id = local_trigram.token_1.wordform,
        first_pos_id = local_trigram.token_1.pos_tag,
        first_sentence_id = local_trigram.token_1.sentence,
        first_start_index = local_trigram.token_1.text_position[0],
        first_end_index = local_trigram.token_1.text_position[1],
        second_lemma_id = local_trigram.token_2.lemma if local_trigram.token_2 else None,
        second_word_form_id = local_trigram.token_2.wordform if local_trigram.token_2 else None,
        second_pos_id = local_trigram.token_2.pos_tag if local_trigram.token_2 else None,
        second_sentence_id = local_trigram.token_2.sentence if local_trigram.token_2 else None,
        second_start_index = local_trigram.token_2.text_position[0] if local_trigram.token_2 else None,
        second_end_index = local_trigram.token_2.text_position[1] if local_trigram.token_2 else None,
        third_lemma_id = local_trigram.token_3.lemma if local_trigram.token_3 else None,
        third_word_form_id = local_trigram.token_3.wordform if local_trigram.token_3 else None,
        third_pos_id = local_trigram.token_3.pos_tag if local_trigram.token_3 else None,
        third_sentence_id = local_trigram.token_3.sentence if local_trigram.token_3 else None,
        third_start_index = local_trigram.token_3.text_position[0] if local_trigram.token_3 else None,
        third_end_index = local_trigram.token_3.text_position[1] if local_trigram.token_3 else None
    )


def fill_db(path: str = str(os.path.join(os.getcwd(), 'instance', 'corpora_past.csv'))):
    session = create_session()
    already_added_items = {'lemma': {}, 'text': {}, 'upos': {}}
    with open(path, 'r', encoding='utf-8') as f:
        for text in tqdm(csv.DictReader(f)):
            text_id = add_class_to_session(session=session, item_class=Texts(text=text['text'], href=text['href']))
            current_trigram = LocalTrigram()
            for sentence in get_text_sentences(text['text']):
                sentence_id = add_class_to_session(session=session, item_class=Sentences(
                    start_index=sentence[0]['start_char'],
                    end_index=sentence[-1]['end_char'],
                    text_id=text_id))
                for token in sentence:
                    if is_a_word(token['text']):
                        token['text'], token['lemma'] = token['text'].lower(), token['lemma'].lower()
                        lemma_id = check_if_exists(
                            session=session,
                            existing_dict=already_added_items,
                            item_type='lemma',
                            stanza_item=token,
                            item_class=Lemmas()
                        )
                        word_form_id = check_if_exists(
                            session=session,
                            existing_dict=already_added_items,
                            item_type='text',
                            stanza_item=token,
                            item_class=WordForms()
                        )
                        pos_id = check_if_exists(
                            session=session,
                            existing_dict=already_added_items,
                            item_type='upos',
                            stanza_item=token,
                            item_class=POS()
                        )
                        current_trigram.move()
                        current_trigram.token_3 = Token(
                            text_position=(token['start_char'], token['end_char']),
                            sentence=sentence_id,
                            wordform=word_form_id,
                            lemma=lemma_id,
                            pos_tag=pos_id)
                        if current_trigram.token_1 is not None:
                            add_class_to_session(session=session, item_class=local_trigram_to_db_class((current_trigram)))
            for i in range(2):
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
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f'В корпусе нет {"леммы" if item_type == "lemma" else "pos-тега" if item_type == "pos" else "словоформы"} {item_val}')


#не доделала ее
def find_trigram(clauses: Dict[str, int]):
    trigrams = select(Trigrams, Sentences)
    for key, item_id in clauses.items():
        trigrams = trigrams.where(getattr(Trigrams, key) == item_id)
    trigrams.join(Sentences)
    print(trigrams)
    session = create_session()
    session.execute(trigrams).all()
    session.close()