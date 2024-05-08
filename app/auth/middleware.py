from fastapi import (HTTPException,
                     Request,
                     status)
from fastapi.responses import RedirectResponse
from jwt import PyJWTError


from app.auth.utils import (verify_token,
                            refresh_access_token)
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

ignore_path = ["/login", "/logout"]
ignore_start = ["/docs", "/openapi.json"]


async def handle_token_refresh(refresh_token, call_next, request):
    try:
        new_access_token = refresh_access_token(refresh_token)
        response = await call_next(request)

        response.set_cookie(key="access_token",
                            value=f"Bearer {new_access_token}",
                            httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        if refresh_token:

            response.set_cookie(key="refresh_token",
                                value=refresh_token,
                                httponly=True,
                                max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60)
        return response

    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            response = RedirectResponse(url="/login")
            response.delete_cookie(key="access_token")
            response.delete_cookie(key="refresh_token")
            return response


async def check_access_token(request: Request, call_next):

    if request.url.path.startswith('/protected'):

        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if access_token:
            try:
                payload = verify_token(access_token, "access_token")
            except HTTPException as e:
                if e.status_code == status.HTTP_401_UNAUTHORIZED:
                    return await handle_token_refresh(refresh_token, call_next, request)
        elif refresh_token:
            return await handle_token_refresh(refresh_token, call_next, request)
        else:
            return RedirectResponse(url="/login")

        response = await call_next(request)
        response.set_cookie(
            "access_token",
            value=f"{access_token}",
            httponly=True,
            secure=True,  # Set secure=True if your site is HTTPS enabled
            samesite='strict',
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        response.set_cookie(
            "refresh_token",
            value=f"{refresh_token}",
            httponly=True,
            secure=True,  # Set secure=True if your site is HTTPS enabled
            samesite='strict',
            max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60
        )

    else:
        response = await call_next(request)

    return response


async def check_user(request: Request):
    refresh_token = request.cookies.get("refresh_token")

    if refresh_token is None:
        return None
    try:
        username = verify_token(refresh_token, "refresh_token")
        return {'username': username}
    except HTTPException:
        return None
    except PyJWTError:
        return None


async def clear_tokens_in_cookies(response: RedirectResponse):

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


async def set_tokens_in_cookies(response: RedirectResponse):

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