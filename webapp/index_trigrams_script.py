from pathlib import Path
from pasta_parser import get_text_trigrams, from_csv
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm
import os

#from db_manager import DataBase

load_dotenv(find_dotenv('login.env'))
csv_data = Path(__file__).parent.joinpath('corpora_past.csv')

counter = 0
pb = tqdm(from_csv(csv_data))
for text, href in pb:
    # text_id = DataBase.insert_text(text, href)
    with open('trigrams.txt', 'a+') as f:
        for trigram in get_text_trigrams(text):
            counter += 1
            f.write(str(trigram) + '\n')
            # DataBase.insert_trigram(trigram, text_id)
        pb.set_description(f"{counter} trigrams")
