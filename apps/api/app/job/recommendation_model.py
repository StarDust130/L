from datetime import UTC, datetime

from app.db.db import Base
from sqlalchemy import DateTime, Float, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Recommendation(Base):
    __tablename__ = "recommendations"

    __table_args__ = (
        UniqueConstraint(
            "clerk_user_id",
            "job_id",
            name="uq_recommendation_user_job",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # 👤 User receiving the recommendation.
    clerk_user_id: Mapped[str] = mapped_column(index=True)

    # 💼 Recommended job.
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        index=True,
    )

    # 🧠 AI's match score.
    match_score: Mapped[float] = mapped_column(Float)

    # 💡 Why AI recommended it.
    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # 🕐 When recommendation was created.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
