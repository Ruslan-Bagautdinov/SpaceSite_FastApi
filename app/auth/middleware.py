from fastapi import (HTTPException,
                     Request,
                     status)
from fastapi.responses import RedirectResponse
from jwt import PyJWTError


from app.auth.utils import (verify_token,
                            refresh_access_token)


async def check_access_token(request: Request, call_next):

    if request.url.path not in ("/", "/login", "/register", "/logout"):

        access_token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")

        if access_token:
            try:
                # Verify the access token
                # payload = verify_token(access_token.split("Bearer ")[1])
                payload = verify_token(access_token)
            except HTTPException as e:
                if e.status_code == status.HTTP_401_UNAUTHORIZED and refresh_token:
                    # If the access token is expired and there is a refresh token, try to refresh it
                    try:
                        new_access_token = refresh_access_token(refresh_token)
                        response = await call_next(request)
                        response.set_cookie(key="access_token", value=f"Bearer {new_access_token}", httponly=True)
                        return response
                    except HTTPException as e:
                        if e.status_code == status.HTTP_401_UNAUTHORIZED:
                            # If the refresh token is expired, redirect to the login page
                            print('OH FUCK ! ! !')
                            return RedirectResponse(url="/")
                else:
                    # If the access token is invalid, redirect to the login page
                    print('OH FUCK ! ! !')
                    return RedirectResponse(url="/")
        else:
            # If there is no access token, redirect to the login page
            print('OH FUCK ! ! !')
            return RedirectResponse(url="/")

    # If the access token is valid, proceed with the request
    response = await call_next(request)
    return response

# async def check_access_token(request: Request):
#     if request.url.path not in ("/", "/login", "/register", "/logout"):
#         access_token = request.cookies.get("access_token")
#         refresh_token = request.cookies.get("refresh_token")
#
#         if access_token:
#             try:
#                 # Verify the access token
#                 payload = verify_token(access_token)
#             except HTTPException as e:
#                 if e.status_code == status.HTTP_401_UNAUTHORIZED and refresh_token:
#                     # If the access token is expired and there is a refresh token, try to refresh it
#                     try:
#                         new_access_token = refresh_access_token(refresh_token)
#                         return new_access_token
#                     except HTTPException as e:
#                         if e.status_code == status.HTTP_401_UNAUTHORIZED:
#                             # If the refresh token is expired, redirect to the login page
#                             raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/"})
#                 else:
#                     # If the access token is invalid, redirect to the login page
#                     raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/"})
#         else:
#             # If there is no access token, redirect to the login page
#             raise HTTPException(status_code=status.HTTP_307_TEMPORARY_REDIRECT, headers={"Location": "/"})
#
#     # If the access token is valid or was refreshed, return the token
#         return access_token


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


