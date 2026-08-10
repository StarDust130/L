from app.telegram.telegram_client import send_message


async def send_test_message(chat_id: str) -> None:
    """Send a test message to a Telegram user."""

    await send_message(
        chat_id=chat_id,
        text="🤖 L is connected.\n\nYour career intelligence system is ready.🔥",
    )
