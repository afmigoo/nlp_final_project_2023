from pathlib import Path
from pasta_parser import get_text_trigrams, from_csv
from dotenv import load_dotenv, find_dotenv
from tqdm import tqdm
import os
load_dotenv(find_dotenv('login.env'))

#from db_manager import DataBase
csv_data = Path(__file__).parent.joinpath('corpora_past.csv')

counter = 0
pb = tqdm(from_csv(csv_data))
for text, href in pb:
    # text_id = DataBase.insert_text(text, href)
    for trigram in get_text_trigrams(text):
        counter += 1
        # DataBase.insert_trigram(trigram, text_id)
    pb.set_description(f"{counter} trigrams")
