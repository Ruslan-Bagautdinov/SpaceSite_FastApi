from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database.postgre_db import engine, Base
from app.routers.users import router as users_router
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
app.include_router(users_router)
app.include_router(protected_router)


@app.get("/", tags=["root"])
async def root():
    return {"message": "Hello World"}
