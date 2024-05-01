from passlib.context import CryptContext
from datetime import datetime, timedelta
from jwt import encode, decode

from app.config import ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token):
    return decode(token, SECRET_KEY, algorithms=[ALGORITHM])
