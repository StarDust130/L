import httpx
from app.core.config import get_settings

settings = get_settings()

TELEGRAM_API_URL = f"https://api.telegram.org/bot{settings.telegram_bot_token}"


async def send_message(
    chat_id: str,
    text: str,
) -> None:
    """Send a message through Telegram."""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{TELEGRAM_API_URL}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text,
            },
        )

        response.raise_for_status()
