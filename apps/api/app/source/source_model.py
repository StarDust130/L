from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Source(Base):
    """🌐 A website/source L can use to discover opportunities."""

    __tablename__ = "sources"

    __table_args__ = (
        UniqueConstraint(
            "url",
            name="uq_source_url",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Example: "Wellfound", "YC Companies"
    name: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    # Main URL L can investigate.
    url: Mapped[str] = mapped_column(
        String(1000),
    )

    # Examples: job_board, company_directory, career_page
    source_type: Mapped[str] = mapped_column(
        String(50),
        index=True,
    )

    # 🧠 How useful this source has proven to be.
    quality_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    # 🕐 Last time we checked this source.
    last_checked: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # 📝 Why L considers this source useful.
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
