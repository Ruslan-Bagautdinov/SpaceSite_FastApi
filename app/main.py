from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager
import sys
from subprocess import check_output
from datetime import datetime
from time import sleep


from app.routers.root import router as root_router
from app.routers.register import router as register_router
from app.routers.login import router as login_router
from app.routers.user import router as user_router


def run_migration_at_start():
    print("Current OS:", sys.platform)
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    output = check_output(
        f'alembic revision --autogenerate -m f"{now}" ',
        shell=True).decode()
    print(output)
    # sleep(5)
    output = check_output(
        f'alembic upgrade head ',
        shell=True).decode()
    print(output)


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migration_at_start()
    yield


app = FastAPI(lifespan=lifespan)


templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(root_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(user_router)
