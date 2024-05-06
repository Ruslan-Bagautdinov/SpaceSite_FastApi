from fastapi import (FastAPI,
                     HTTPException,
                     Depends,
                     Response,
                     Request,
                     status)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from typing import Optional
import jwt

from contextlib import asynccontextmanager
from subprocess import call
from datetime import datetime
from time import sleep

from app.auth.utils import verify_token, refresh_access_token
from app.routers.root import router as root_router
from app.routers.register import router as register_router
from app.routers.login import router as login_router
from app.routers.profile import router as profile_router


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
                            return RedirectResponse(url="/")
                else:
                    # If the access token is invalid, redirect to the login page
                    return RedirectResponse(url="/")
        else:
            # If there is no access token, redirect to the login page
            return RedirectResponse(url="/")

        # If the access token is valid, proceed with the request
        response = await call_next(request)
        return response
