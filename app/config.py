from os import getenv, path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SECRET_KEY = getenv('SECRET_KEY')
ALGORITHM = getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_MINUTES = int(getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))

PG_DB_HOST = getenv('PG_DB_HOST')
PG_DB_PORT = getenv('PG_DB_PORT')
PG_DB_USER = getenv('PG_DB_USER')
PG_DB_PASSWORD = getenv('PG_DB_PASSWORD')
PG_DB_NAME = getenv('PG_DB_NAME')

UNSPLASH_ACCESS_KEY = getenv('UNSPLASH_ACCESS_KEY')

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
IMAGE_DIR = path.join(BASE_DIR, 'photo')
