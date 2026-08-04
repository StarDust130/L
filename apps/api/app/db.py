from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# 💾 Connect to the database
engine = create_async_engine(
    settings.database_url,
    echo=False,
)

# 🧰 Create database sessions
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # 🔌 Give one database session to one request
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    # 🏗️ Create tables during local development

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
