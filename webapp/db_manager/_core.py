import psycopg2
from typing import List

from pasta_parser import Token

class DataBase:
    def __init__(self, host: str, port, user: str, password: str) -> None:
        self.conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port
        )
    
    def put_text(self, text: str, tokens: List[Token]) -> bool:
        pass