import logging

from app.agent.agent_service import run_agent
from app.telegram.telegram_client import send_message

logger = logging.getLogger(__name__)


async def send_test_message(chat_id: str) -> None:
    """Send a test message to a Telegram user."""

    await send_message(
        chat_id=chat_id,
        text="🤖 L is connected.\n\nYour career intelligence system is ready.🔥",
    )


async def handle_telegram_message(
    chat_id: str,
    message: str,
) -> None:
    """Process an incoming Telegram message."""

    logger.info(
        "📱 telegram_message_received chat_id=%s",
        chat_id,
    )

    # 🤖 Send the user's message to our agent.
    response = await run_agent(message)

    # 📤 Send the agent's response back to Telegram.
    await send_message(
        chat_id=chat_id,
        text=response,
    )

    logger.info(
        "📱 telegram_response_sent chat_id=%s",
        chat_id,
    )
