from app.db.db import Base
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Job(Base):
    __tablename__ = "jobs"

    # 🆔 Our database ID.
    id: Mapped[int] = mapped_column(primary_key=True)

    # 🔑 ID provided by the job source.
    external_id: Mapped[str] = mapped_column(String(100))

    title: Mapped[str] = mapped_column(String(255))
    company: Mapped[str] = mapped_column(String(255))
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(255), nullable=True)
    

    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # 🔗 Where the user actually applies.
    apply_url: Mapped[str] = mapped_column(String(1000))

    # 🌐 Where we collected the job from.
    source: Mapped[str] = mapped_column(String(50))
