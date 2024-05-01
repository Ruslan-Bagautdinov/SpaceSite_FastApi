from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from ..config import PG_DB_USER, PG_DB_PASSWORD, PG_DB_HOST, PG_DB_NAME

DATABASE_URL = (f"postgresql+asyncpg"
                f"://{PG_DB_USER}"
                f":{PG_DB_PASSWORD}"
                f"@{PG_DB_HOST}"
                f"/{PG_DB_NAME}")

engine = create_async_engine(DATABASE_URL)

async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
