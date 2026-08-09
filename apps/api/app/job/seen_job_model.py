from datetime import UTC, datetime

from app.db.db import Base
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class SeenJob(Base):
    __tablename__ = "seen_jobs"

    __table_args__ = (
        UniqueConstraint(
            "clerk_user_id",
            "job_id",
            name="uq_seen_job_user_job",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # 👤 User who saw the job.
    clerk_user_id: Mapped[str] = mapped_column(index=True)

    # 💼 Job they saw.
    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        index=True,
    )

    # 🕐 When they saw it.
    seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
