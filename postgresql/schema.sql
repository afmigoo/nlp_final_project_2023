CREATE TABLE IF NOT EXISTS texts (
    id                  SERIAL PRIMARY KEY,
    content             TEXT
);

CREATE TABLE IF NOT EXISTS ngrams (
    ngram               TEXT PRIMARY KEY,
    text_id             integer NOT NULL REFERENCES texts(id),
    begin_idx           integer NOT NULL,
    end_idx             integer NOT NULL
);

CREATE INDEX IF NOT EXISTS ngram_index ON ngrams (ngram);