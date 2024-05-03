from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from contextlib import asynccontextmanager

from app.database.postgre_db import engine, Base
from app.routers.root import router as root_router
from app.routers.register import router as register_router
from app.routers.login import router as login_router
from app.routers.protected import router as protected_router



async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown():
    print('Shutting down...')
    return {"message": "Shutting down..."}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await shutdown()


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(root_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(protected_router)
