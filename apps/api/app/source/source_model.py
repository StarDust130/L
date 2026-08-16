from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    url: Mapped[str] = mapped_column(
        String(1000),
        unique=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )

    quality_score: Mapped[float] = mapped_column(
        default=0.0,
    )

    # 🕐 When we last checked this source.
    last_checked: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ❌ How many consecutive failures.
    failure_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
