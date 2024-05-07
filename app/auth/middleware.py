from fastapi import (HTTPException,
                     Request,
                     status)
from fastapi.responses import RedirectResponse
from jwt import PyJWTError


from app.auth.utils import (verify_token,
                            refresh_access_token)

ignore_path = ("/", "/login", "/register", "/logout")
ignore_start = ("/docs", "/openapi.json", "/redoc")


async def check_access_token(request: Request, call_next):

    if request.url.path in ignore_path or any(request.url.path.startswith(path) for path in ignore_start):
        pass
    else:
        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if access_token:
            try:
                payload = verify_token(access_token)
            except HTTPException as e:
                if e.status_code == status.HTTP_401_UNAUTHORIZED and refresh_token:
                    try:
                        new_access_token = refresh_access_token(refresh_token)
                        response = await call_next(request)
                        response.set_cookie(key="access_token", value=f"Bearer {new_access_token}", httponly=True)
                        return response
                    except HTTPException as e:
                        if e.status_code == status.HTTP_401_UNAUTHORIZED:
                            return RedirectResponse(url="/")
                else:
                    return RedirectResponse(url="/")
        else:
            return RedirectResponse(url="/")

    response = await call_next(request)
    return response


async def check_user(request: Request):
    access_token = request.cookies.get("access_token")

    if access_token is None:
        return None
    try:
        username = verify_token(access_token)
        return {'username': username}
    except HTTPException:
        return None
    except PyJWTError:
        return None


