import logging
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.memory.memory_model import UserMemory

logger = logging.getLogger(__name__)


async def get_memory(
    db: AsyncSession,
    user_id: str,
) -> dict[str, Any]:
    """
    Get the user's long-term memory.

    Returns an empty dict when the user has no memory yet.
    """

    result = await db.execute(
        select(UserMemory).where(
            UserMemory.clerk_user_id == user_id,
        )
    )

    memory = result.scalar_one_or_none()

    if memory is None:
        return {}

    return memory.memory




async def save_memory(
    db: AsyncSession,
    user_id: str,
    memory_data: dict[str, Any],
) -> dict[str, Any]:
    """Create or update the user's long-term memory."""

    logger.info(
        "🧠 save_memory started | user=%s | data=%s",
        user_id,
        memory_data,
    )

    result = await db.execute(
        select(UserMemory).where(
            UserMemory.clerk_user_id == user_id,
        )
    )

    memory = result.scalar_one_or_none()

    if memory is None:
        logger.info("🆕 Creating new memory row")

        memory = UserMemory(
            clerk_user_id=user_id,
            memory=memory_data,
        )

        db.add(memory)

    else:
        logger.info(
            "♻️ Updating existing memory row | id=%s",
            memory.id,
        )

        current_memory = memory.memory or {}
        current_memory.update(memory_data)
        memory.memory = current_memory

    await db.commit()
    await db.refresh(memory)

    logger.info(
        "✅ Memory saved successfully | id=%s | memory=%s",
        memory.id,
        memory.memory,
    )

    return memory.memory
