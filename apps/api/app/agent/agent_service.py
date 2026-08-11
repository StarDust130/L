import logging

from app.core.config import get_settings
from app.llm.client import client

logger = logging.getLogger(__name__)

settings = get_settings()


async def run_agent(
    message: str,
    user_id: str,
) -> str:
    """🤖 Run L for an authenticated user."""

    logger.info(
        "🤖 agent_request_received user_id=%s",
        user_id,
    )

    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are L, a private career intelligence assistant. "
                    "Be concise, useful, and direct. "
                    "Format responses for Telegram mobile chat. "
                    "Use short paragraphs and simple bullet points. "
                    "Use emojis when useful. "
                    "Do not use Markdown tables. "
                    "Do not use long walls of text. "
                    "Keep responses easy to scan."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("LLM returned an empty response")

    logger.info(
        "🤖 agent_response_created user_id=%s",
        user_id,
    )

    return content
