from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings


settings = get_settings()


# 💾 Async database engine
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
)


# 🧰 Database session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# 🏗️ Base class for all SQLAlchemy models
class Base(DeclarativeBase):
    pass


# 🔌 Provide one database session per request/task
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# 🛑 No create_all() here.
#
# Database schema is managed by Alembic migrations.