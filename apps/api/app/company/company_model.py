from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.db import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 🏢 Basic company information.
    name: Mapped[str] = mapped_column(String(255), index=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # 🔗 Optional source/company identifier.
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
