from app.telegram.telegram_service import handle_telegram_message, send_test_message
from fastapi import APIRouter, Request

router = APIRouter(prefix="/telegram", tags=["Telegram"])


@router.post("/test")
async def test_telegram(chat_id: str):
    """Test Telegram connection."""

    await send_test_message(chat_id)

    return {
        "status": "sent",
    }


router = APIRouter(
    prefix="/telegram",
    tags=["Telegram"],
)


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Receive updates from Telegram."""

    update = await request.json()

    # 📨 Ignore updates that don't contain a text message.
    message = update.get("message")

    if not message:
        return {"status": "ignored"}

    text = message.get("text")

    if not text:
        return {"status": "ignored"}

    chat_id = str(message["chat"]["id"])

    # 🤖 Process the message.
    await handle_telegram_message(
        chat_id=chat_id,
        message=text,
    )

    return {"status": "ok"}
