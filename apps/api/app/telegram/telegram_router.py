from app.telegram.telegram_service import send_test_message
from fastapi import APIRouter

router = APIRouter(prefix="/telegram", tags=["Telegram"])


@router.post("/test")
async def test_telegram(chat_id: str):
    """Test Telegram connection."""

    await send_test_message(chat_id)

    return {
        "status": "sent",
    }
