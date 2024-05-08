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
        # Create a new response object to avoid modifying the original response
        response = await call_next(request)
        # Set the new access token cookie on the response
        response.set_cookie(key="access_token", value=f"Bearer {new_access_token}", httponly=True, max_age=1800)  # 30 minutes
        # Set the refresh token cookie on the response if it exists
        if refresh_token:
            response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)  # No max_age, so it's a session cookie
        return response
    except HTTPException as e:
        if e.status_code == status.HTTP_401_UNAUTHORIZED:
            # Handle refresh token expiration or invalidity
            # Clear the cookies on the response
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
                    # Handle access token expiration
                    return await handle_token_refresh(refresh_token, call_next, request)
        elif refresh_token:
            # Handle the case where the access token is not present but the refresh token is
            return await handle_token_refresh(refresh_token, call_next, request)
        else:
            # Neither token is present, redirect to login
            return RedirectResponse(url="/login")

        # If the access token is valid, proceed with the request
        response = await call_next(request)
        # Ensure the cookies are set on the response
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


