from os import getenv, path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SECRET_KEY = getenv('SECRET_KEY')
ALGORITHM = getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
REFRESH_TOKEN_EXPIRE_MINUTES = int(getenv('REFRESH_TOKEN_EXPIRE_MINUTES'))

POSTGRES_HOST = getenv('POSTGRES_HOST')
POSTGRES_PORT = getenv('POSTGRES_PORT')
POSTGRES_USER = getenv('POSTGRES_USER')
POSTGRES_PASSWORD = getenv('POSTGRES_PASSWORD')
POSTGRES_DB = getenv('POSTGRES_DB')

UNSPLASH_ACCESS_KEY = getenv('UNSPLASH_ACCESS_KEY')

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
IMAGE_DIR = path.join(BASE_DIR, 'photo')

DATABASE_URL = (f"mysql+pymysql"
                f"://{POSTGRES_USER}"
                f":{POSTGRES_PASSWORD}"
                f"@{POSTGRES_HOST}"
                f"/{POSTGRES_DB}")
