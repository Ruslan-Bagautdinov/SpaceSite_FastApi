from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware
from contextlib import asynccontextmanager

from subprocess import call
from datetime import datetime
from time import sleep


from app.routers.root import router as root_router
from app.routers.register import router as register_router
from app.routers.login import router as login_router
from app.routers.profile import router as profile_router
from app.auth.middleware import check_access_token
from app.config import SECRET_KEY, BASE_DIR


def run_migration_at_start():

    #  first time rin in shell: alembic init -t async alembic

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
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
app.middleware("http")(check_access_token)

templates = Jinja2Templates(directory=f"{BASE_DIR}/templates")
app.mount("/static", StaticFiles(directory=f"{BASE_DIR}/static"), name="static")


app.include_router(root_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(profile_router)
