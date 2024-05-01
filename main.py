from fastapi import FastAPI
from contextlib import asynccontextmanager

from routers.users import router as users_router
from database.postgre_db import engine, Base


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def shutdown():
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await shutdown()


app = FastAPI(lifespan=lifespan)
app.include_router(users_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
