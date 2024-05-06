from os import getenv
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = getenv('SECRET_KEY')
ALGORITHM = getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = getenv('ACCESS_TOKEN_EXPIRE_MINUTES')
REFRESH_TOKEN_EXPIRE_MINUTES = getenv('REFRESH_TOKEN_EXPIRE_MINUTES')

PG_DB_HOST = getenv('PG_DB_HOST')
PG_DB_PORT = getenv('PG_DB_PORT')
PG_DB_USER = getenv('PG_DB_USER')
PG_DB_PASSWORD = getenv('PG_DB_PASSWORD')
PG_DB_NAME = getenv('PG_DB_NAME')
