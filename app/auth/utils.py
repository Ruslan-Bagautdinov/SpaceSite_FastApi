from fastapi import (Request,
                     HTTPException,
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

from app.tools.functions import redirect_with_message
from templates.icons import OK_CLASS, OK_ICON

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


def create_token(user_name: str, token_type: str, expire_delta: int):
    expire = datetime.utcnow() + timedelta(minutes=expire_delta)
    data = {
        "user_name": user_name,
        "exp": expire,
        "Expires": expire.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        "Max-Age": expire_delta * 60,
        "type": token_type
    }

    encoded_token = encode(data, SECRET_KEY, algorithm=ALGORITHM)
    # encoded_token = b64encode(encoded_jwt).decode('utf-8')  # use with PyJWT==1.7.1
    return encoded_token


def create_access_token(user_name: str):
    return create_token(user_name, "access_token", ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(user_name: str):
    return create_token(user_name, "refresh_token", REFRESH_TOKEN_EXPIRE_MINUTES)


def decode_token(token):
    token = token.replace("Bearer ", "")
    # token = b64decode(token).decode('utf-8') # use with PyJWT==1.7.1
    return decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def verify_token(token: str, token_type: str):
    try:
        payload = decode_token(token)
        if payload['type'] == token_type:
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


def set_tokens_in_cookies(response: RedirectResponse,
                          access_token: str | None = None,
                          refresh_token: str | None = None):

    if access_token:
        response.set_cookie(
            "access_token",
            value=f"{access_token}",
            httponly=True,
            secure=True,  # Set secure=True if your site is HTTPS enabled
            samesite='strict',
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

    if refresh_token:
        response.set_cookie(
            "refresh_token",
            value=f"{refresh_token}",
            httponly=True,
            secure=True,  # Set secure=True if your site is HTTPS enabled
            samesite='strict',
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60
        )
    return response


def clear_tokens_in_cookies(response: RedirectResponse):

    response.set_cookie(
        "access_token",
        value="",
        httponly=True,
        max_age=0,
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
        path="/",
        domain=None,
        secure=False,
        samesite="lax"
    )

    response.set_cookie(
        "refresh_token",
        value="",
        httponly=True,
        max_age=0,
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
        path="/",
        domain=None,
        secure=False,
        samesite="lax"
    )
    return response


async def authenticated_root_redirect(request: Request, username: str):

    access_token = create_access_token(username)
    refresh_token = create_refresh_token(username)

    response = await redirect_with_message(request=request,
                                           message_class=OK_CLASS,
                                           message_icon=OK_ICON,
                                           message_text=f"You are logged in with the account: {username}",
                                           endpoint="/")
    response = set_tokens_in_cookies(response, access_token, refresh_token)

    return response
