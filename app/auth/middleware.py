from fastapi import (HTTPException,
                     Request,
                     status)
from fastapi.responses import RedirectResponse
from jwt import PyJWTError


from app.auth.utils import (verify_token,
                            refresh_access_token,
                            set_tokens_in_cookies)

ignore_path = ["/login", "/logout"]
ignore_start = ["/docs", "/openapi.json"]


async def handle_token_refresh(refresh_token, call_next, request):
    try:
        new_access_token = refresh_access_token(refresh_token)
        response = await call_next(request)

        response = await set_tokens_in_cookies(response, access_token=new_access_token)
        # response.set_cookie(key="access_token",
        #                     value=f"Bearer {new_access_token}",
        #                     httponly=True, max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60)

        if refresh_token:

            response = await set_tokens_in_cookies(response, refresh_token=refresh_token)

            # response.set_cookie(key="refresh_token",
            #                     value=refresh_token,
            #                     httponly=True,
            #                     max_age=REFRESH_TOKEN_EXPIRE_MINUTES * 60)
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

        response = await set_tokens_in_cookies(response, access_token, refresh_token)

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
