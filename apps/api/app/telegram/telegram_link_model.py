from datetime import datetime

from app.db.db import Base
from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


class TelegramLinkToken(Base):
    __tablename__ = "telegram_link_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)

    # 📱 Telegram chat waiting to be linked.
    telegram_chat_id: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )

    # 🔑 Random one-time token.
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
    )

    # ⏳ Token expires quickly.
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
    )

    # ✅ Prevent token reuse.
    used: Mapped[bool] = mapped_column(
        default=False,
    )
