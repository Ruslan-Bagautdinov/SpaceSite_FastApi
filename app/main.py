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

from app.auth.middleware import check_access_token
from app.routers.root import router as root_router
from app.routers.register import router as register_router
from app.routers.login import router as login_router
from app.routers.profile import router as profile_router


def run_migration_at_start():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print('. . . Revision started. . . ')
    call(f'alembic revision --autogenerate -m f"{now}" ', shell=True)
    print('. . . Revision finished. . . ')
    sleep(2)
    print('. . . Migration started. . . ')
    call(f'alembic upgrade head ', shell=True)
    print('. . . Migration finished. . . ')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # run_migration_at_start()
    yield


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# app.middleware("http")(check_access_token)
app.include_router(root_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(profile_router)


