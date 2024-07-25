from os import getenv, path
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

SECRET_KEY = getenv('SECRET_KEY', 'secret-key')
ALGORITHM = getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
REFRESH_TOKEN_EXPIRE_MINUTES = int(getenv('REFRESH_TOKEN_EXPIRE_MINUTES', '10080'))

POSTGRES_HOST = getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = getenv('POSTGRES_PORT', '5432')
POSTGRES_USER = getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = getenv('POSTGRES_PASSWORD', 'password')
POSTGRES_DB = getenv('POSTGRES_DB', 'database')

DATABASE_URL = (f"postgresql+asyncpg"
                f"://{POSTGRES_USER}"
                f":{POSTGRES_PASSWORD}"
                f"@{POSTGRES_HOST}"
                f":{POSTGRES_PORT}"
                f"/{POSTGRES_DB}")

UNSPLASH_ACCESS_KEY = getenv('UNSPLASH_ACCESS_KEY', 'unsplash-access-key')

BASE_DIR = path.dirname(path.dirname(path.abspath(__file__)))
IMAGE_DIR = path.join(BASE_DIR, 'photo')
