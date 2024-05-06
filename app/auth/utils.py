from fastapi import (HTTPException,
                     status)
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext

from datetime import datetime, timedelta
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from base64 import b64encode, b64decode

from app.config import (ALGORITHM,
                        SECRET_KEY,
                        ACCESS_TOKEN_EXPIRE_MINUTES,
                        REFRESH_TOKEN_EXPIRE_MINUTES
                        )


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_token(user_name: str, token_type: str, expire_delta: str):

    data = {
            "user_name": user_name,
            "exp": datetime.utcnow() + timedelta(minutes=eval(expire_delta)),
            "type": token_type
    }

    encoded_jwt = encode(data, SECRET_KEY, algorithm=ALGORITHM)
    encoded_token = b64encode(encoded_jwt).decode('utf-8')
    return encoded_token


def create_access_token(user_name: str):
    return create_token(user_name, "access_token", ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(user_name: str):
    return create_token(user_name, "refresh_token", REFRESH_TOKEN_EXPIRE_MINUTES)


def decode_token(token):
    token = token.replace("Bearer ", "")
    token = b64decode(token).decode('utf-8')
    return decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_token(token: str):
    try:
        payload = decode_token(token)
        if payload['type'] == 'access_token':
            return payload['user_name']
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def refresh_access_token(refresh_token: str):
    try:
        payload = decode_token(refresh_token)
        if payload['type'] == 'refresh_token':
            user_name = payload['user_name']
            new_access_token = create_access_token(user_name)
            return new_access_token
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")


def authenticated_root_redirect(username: str):
    access_token = create_access_token(username)
    refresh_token = create_refresh_token(username)

    response = RedirectResponse(url="/",
                                status_code=status.HTTP_302_FOUND
                                )

    response.set_cookie(
        "access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=False,
        samesite='lax'
    )

    response.set_cookie(
        "refresh_token",
        value=f"Bearer {refresh_token}",
        httponly=True,
        secure=False,
        samesite='lax'
    )
    return response
