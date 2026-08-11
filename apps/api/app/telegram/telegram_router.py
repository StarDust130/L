from datetime import UTC, datetime

from app.core.auth import require_user
from app.db.db import get_db
from app.telegram.telegram_account_model import TelegramAccount
from app.telegram.telegram_link_model import TelegramLinkToken
from app.telegram.telegram_service import handle_telegram_message
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/telegram", tags=["Telegram"])


# Telegram bot webhook endpoint to receive messages.
@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Receive Telegram updates."""

    update = await request.json()

    message = update.get("message")

    if not message:
        return {"status": "ignored"}

    text = message.get("text")

    if not text:
        return {"status": "ignored"}

    chat = message["chat"]

    chat_id = str(chat["id"])
    username = chat.get("username")

    await handle_telegram_message(
        db=db,
        chat_id=chat_id,
        message=text,
        username=username,
    )

    return {"status": "ok"}


# Connect Telegram bot to L account via Clerk.

@router.post("/connect")
async def connect_telegram(
    token: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(require_user),
):
    """Connect Telegram to the authenticated L account."""

    # 🔑 Find the temporary linking token.
    result = await db.execute(
        select(TelegramLinkToken).where(
            TelegramLinkToken.token == token,
            TelegramLinkToken.used.is_(False),
        )
    )

    link_token = result.scalar_one_or_none()

    if link_token is None:
        raise HTTPException(
            status_code=400,
            detail="Invalid or already used link token",
        )

    # ⏳ Check expiration.
    if link_token.expires_at < datetime.now(UTC):
        raise HTTPException(
            status_code=400,
            detail="Link token expired",
        )

    # 🔍 Check whether this Telegram account is already linked.
    result = await db.execute(
        select(TelegramAccount).where(
            TelegramAccount.telegram_chat_id == link_token.telegram_chat_id
        )
    )

    existing_account = result.scalar_one_or_none()

    if existing_account:
        # 👤 Same L account → safe/idempotent.
        if existing_account.clerk_user_id == user_id:
            link_token.used = True
            await db.commit()

            return {
                "status": "already_connected",
            }

        # 🛑 Different L account → never silently replace it.
        raise HTTPException(
            status_code=409,
            detail="Telegram is already connected to another L account",
        )

    # 🔗 Create the connection.
    db.add(
        TelegramAccount(
            clerk_user_id=user_id,
            telegram_chat_id=link_token.telegram_chat_id,
        )
    )

    # 🚫 Token can only be used once.
    link_token.used = True

    await db.commit()

    return {
        "status": "connected",
    }


# # TODO:
# And eventually add:

# TelegramAccount
#     ↓
# linked_at
# last_seen_at

# and maybe:

# unlinked_at