from datetime import UTC, datetime

from app.db.db import Base
from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class CandidateProfileRecord(Base):
    __tablename__ = "candidate_profiles"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    # 🔐 Connect database data to the Clerk user
    clerk_user_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    # 📦 Store the validated profile as JSON
    profile: Mapped[dict] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )


"""
One Clerk user → one candidate profile row
"""
