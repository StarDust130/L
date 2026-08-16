from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(255), index=True)

    # 🌐 Company's real website.
    website: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # 🏢 Where the company is based.
    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # 🧠 Short company description.
    description: Mapped[str | None] = mapped_column(
        String(2000),
        nullable=True,
    )

    # 🎓 YC batch, e.g. S2024 / W2025.
    yc_batch: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # 👥 Current team size if available.
    employee_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # ✅ Active / inactive company.
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
    )

    # 💼 Whether we currently see hiring activity.
    is_hiring: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
    )

    # 🔗 Source identity.
    source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
