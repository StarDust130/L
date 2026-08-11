from app.core.auth import require_user
from app.db.db import get_db
from app.telegram.telegram_service import (
    create_link_code,
    handle_telegram_message,
)
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/telegram",
    tags=["Telegram"],
)


@router.post("/link-code")
async def create_telegram_link_code(
    db: AsyncSession = Depends(get_db),
    clerk_user_id: str = Depends(require_user),
):
    """🔑 Create a temporary Telegram connection code."""

    return await create_link_code(
        db=db,
        clerk_user_id=clerk_user_id,
    )


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """📥 Receive Telegram updates."""

    update = await request.json()

    message = update.get("message")

    if not message:
        return {"status": "ignored"}

    text = message.get("text")

    if not text:
        return {"status": "ignored"}

    chat_id = str(message["chat"]["id"])

    await handle_telegram_message(
        db=db,
        chat_id=chat_id,
        message=text,
    )

    return {"status": "ok"}
