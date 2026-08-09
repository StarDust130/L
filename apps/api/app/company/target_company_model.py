from app.db.db import Base
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class TargetCompany(Base):
    __tablename__ = "target_companies"

    __table_args__ = (
        UniqueConstraint(
            "clerk_user_id",
            "company_id",
            name="uq_target_company_user_company",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # 👤 Which user wants this company?
    clerk_user_id: Mapped[str] = mapped_column(index=True)

    # 🏢 Which company?
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id"),
        index=True,
    )
