from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

database_url = os.getenv('DATABASE_URL')
vk_access_token = os.getenv('TOKEN_USER')
vk_version = os.getenv('VERSION')
vk_page = os.getenv('DOMAIN')

engine = create_engine(database_url)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
