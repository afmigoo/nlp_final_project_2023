from pathlib import Path
from pasta_parser import parse_text
from pprint import pprint
from dotenv import load_dotenv, find_dotenv
import os
load_dotenv(find_dotenv('login.env'))

from db_manager import DataBase

data_file_path = Path(__file__).parent.joinpath('pastas.txt')
separator = '<|endoftext|>'

def load_texts(path=data_file_path):
    with open(path, 'r', encoding='utf-8') as f:
        current_text = ''
        for line in f:
            if separator in line:
                yield current_text
                current_text = ''
            else:
                if line != '\n': current_text += '\n' + line
        yield current_text

for t in load_texts():
    tokens = list(parse_text(t))
