from fastapi import APIRouter, Depends, Request  # 🚀 FastAPI tools
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 Async database session

from app.core.auth import require_user  # 🔐 Get the logged-in user
from app.db.db import get_db  # 🗄️ Get database session
from app.telegram.telegram_service import (
    create_link_code,  # 🔑 Create Telegram link code
    handle_telegram_message,  # 📥 Process Telegram message
)

# 📱 Telegram API routes
router = APIRouter(
    prefix="/telegram",
    tags=["Telegram"],
)


# 🔑 Create a OTP code to connect Telegram
@router.post("/link-code")
async def create_telegram_link_code(
    db: AsyncSession = Depends(get_db),
    clerk_user_id: str = Depends(require_user),
):
    # 🔑 Create link code for the current user
    return await create_link_code(
        db=db,
        clerk_user_id=clerk_user_id,
    )


# 📥 Receive and process Telegram webhook updates
@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    #1️⃣) 📦 Read Telegram update
    update = await request.json()

    #2️⃣) 💬 Get message from update
    message = update.get("message")

    # ⏭️ Ignore updates without messages
    if not message:
        return {"status": "ignored"}

    #3️⃣) 📝 Get message text
    text = message.get("text")

    # ⏭️ Ignore messages without text
    if not text:
        return {"status": "ignored"}

    #4️⃣) 🆔 Get Telegram chat ID
    chat_id = str(message["chat"]["id"])

    # 🤖 Process the Telegram message
    await handle_telegram_message(
        db=db,
        chat_id=chat_id,
        message=text,
    )

    # ✅ Tell Telegram the webhook was processed
    return {"status": "ok"}
