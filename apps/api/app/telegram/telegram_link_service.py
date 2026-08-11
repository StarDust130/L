import secrets
from datetime import UTC, datetime, timedelta

from app.telegram.telegram_link_model import TelegramLinkToken
from sqlalchemy.ext.asyncio import AsyncSession


async def create_link_token(
    db: AsyncSession,
    telegram_chat_id: str,
) -> str:
    """Create a short-lived Telegram account linking token."""

    token = secrets.token_urlsafe(32)

    link_token = TelegramLinkToken(
        telegram_chat_id=telegram_chat_id,
        token=token,
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )

    db.add(link_token)

    await db.commit()

    return token
