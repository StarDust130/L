from datetime import UTC, datetime

from app.db.db import Base
from sqlalchemy import DateTime, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class TelegramAccount(Base):
    __tablename__ = "telegram_accounts"

    __table_args__ = (
        UniqueConstraint( 
            "clerk_user_id",
            name="uq_telegram_account_clerk_user",
        ),
        UniqueConstraint(
            "telegram_chat_id",
            name="uq_telegram_account_chat",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # 🔐 L user identity.
    clerk_user_id: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    # 📱 Telegram identity.
    telegram_chat_id: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    telegram_username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    linked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )
