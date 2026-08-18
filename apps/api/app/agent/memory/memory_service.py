from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.memory.memory_model import UserMemory


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
    """
    Create or update the user's long-term memory.

    New memory data is merged into the existing memory.
    """

    result = await db.execute(
        select(UserMemory).where(
            UserMemory.clerk_user_id == user_id,
        )
    )

    memory = result.scalar_one_or_none()

    if memory is None:
        memory = UserMemory(
            clerk_user_id=user_id,
            memory=memory_data,
        )

        db.add(memory)

    else:
        current_memory = memory.memory or {}
        current_memory.update(memory_data)
        memory.memory = current_memory

    await db.commit()
    await db.refresh(memory)

    return memory.memory
