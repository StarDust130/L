import logging

from app.agent.agent_service import run_agent
from app.core.config import get_settings
from app.telegram.telegram_client import send_message
from app.telegram.telegram_link_service import create_link_token
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
settings = get_settings()


async def send_test_message(chat_id: str) -> None:
    """Send a test message to a Telegram user."""

    await send_message(
        chat_id=chat_id,
        text="🤖 L is connected.\n\nYour career intelligence system is ready.🔥",
    )


async def handle_telegram_message(
    db: AsyncSession,
    chat_id: str,
    message: str,
    username: str | None = None,
) -> None:

    if message == "/start":
        token = await create_link_token(
            db=db,
            telegram_chat_id=chat_id,
        )

        link_url = f"{settings.frontend_url}/telegram/connect?token={token}"

        await send_message(
            chat_id=chat_id,
            text=(
                "👋 Welcome to L.\n\n"
                "Connect your L account first:\n\n"
                f"{link_url}\n\n"
                "🔐 This link expires in 10 minutes."
            ),
        )

        return

    # 🤖 Normal messages continue to the agent.
    response = await run_agent(message)

    await send_message(
        chat_id=chat_id,
        text=response,
    )
