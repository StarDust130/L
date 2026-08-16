from app.db.db import Base
from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Job(Base):
    """📋 Job listing model - stores job postings from various sources"""

    __tablename__ = "jobs"
    __table_args__ = (
        # 🔑 Ensure each source has unique job IDs
        UniqueConstraint(
            "source",
            "external_id",
            name="uq_job_source_external_id",
        ),
    )

    # 🆔 Primary key
    id: Mapped[int] = mapped_column(primary_key=True)

    # 🏷️ Job ID from external source (LinkedIn, Indeed, etc.)
    external_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # 🧬 Used to detect the same job across different sources.
    fingerprint: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    # 💼 Job title
    title: Mapped[str] = mapped_column(String(255))

    # 🏢 Company name
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )

    # 📍 Job location (optional)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 📝 Full job description (optional)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 💰 Salary info (optional)
    salary: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 🔗 Application URL
    apply_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # 📌 Source platform (LinkedIn, Indeed, etc.)
    source: Mapped[str] = mapped_column(String(50))
