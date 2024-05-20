from sqlalchemy.ext.asyncio import (AsyncSession,
                                    async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import declarative_base


from app.config import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_DB

DATABASE_URL = (f"postgresql+asyncpg"
                f"://{POSTGRES_USER}"
                f":{POSTGRES_PASSWORD}"
                f"@{POSTGRES_HOST}"
                f"/{POSTGRES_DB}")

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
