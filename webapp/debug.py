from db_manager import Base, engine, fill_db, find_trigram

Base.metadata.create_all(engine)
#fill_db('webapp/instance/corpora_past.csv')
find_trigram({
    "first_lemma_id": 127
})