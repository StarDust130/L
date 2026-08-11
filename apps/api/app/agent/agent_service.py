import logging

from app.core.config import get_settings
from app.llm.client import client

logger = logging.getLogger(__name__)

settings = get_settings()


async def run_agent(message: str) -> str:
    """Send a user message to the LLM and return its response."""

    logger.info("🤖 agent_request_received")

    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are L, a private career intelligence assistant. "
                    "Be concise, useful, and direct."
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

    logger.info("🤖 agent_response_created")

    return content
