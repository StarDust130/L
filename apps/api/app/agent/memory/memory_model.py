from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class UserMemory(Base):
    __tablename__ = "user_memories"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    clerk_user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    memory: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
