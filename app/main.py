from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager

from alembic.config import Config
from alembic import command
import asyncio
from alembic.runtime.migration import MigrationContext

from app.database.postgre_db import engine, get_session
from app.routers.root import router as root_router
from app.routers.register import router as register_router
from app.routers.login import router as login_router
from app.routers.user import router as user_router


# async def create_tables():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


async def run_migrations():
    alembic_cfg = Config("alembic.ini")
    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: command.upgrade(alembic_cfg, "head"))


async def shutdown():
    print('Shutting down...')
    return {"message": "Shutting down..."}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await run_migrations()
    yield
    await shutdown()


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(root_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(user_router)
