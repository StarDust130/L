from collections.abc import AsyncGenerator

from app.core.config import get_settings
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

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

# Look at all my SQLAlchemy models and create their tables if they don't exist.
async def init_db() -> None:
    # 🏗️ Create tables during local development

    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
