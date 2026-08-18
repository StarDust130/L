import logging
from copy import deepcopy
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


def merge_memory(
    old: dict[str, Any],
    new: dict[str, Any],
) -> dict[str, Any]:
    """
    Deep-merge new memory into existing memory.

    Nested dictionaries are merged instead of replaced.
    """

    result = deepcopy(old)

    for key, value in new.items():
        if isinstance(result.get(key), dict) and isinstance(value, dict):
            result[key] = merge_memory(
                result[key],
                value,
            )
        else:
            result[key] = deepcopy(value)

    return result


async def save_memory(
    db: AsyncSession,
    user_id: str,
    memory_data: dict[str, Any],
) -> dict[str, Any]:
    """Create or update the user's long-term memory."""

    result = await db.execute(
        select(UserMemory).where(
            UserMemory.clerk_user_id == user_id,
        )
    )

    memory = result.scalar_one_or_none()

    if memory is None:
        memory = UserMemory(
            clerk_user_id=user_id,
            memory=deepcopy(memory_data),
        )

        db.add(memory)

    else:
        current_memory = merge_memory(
            memory.memory or {},
            memory_data,
        )

        memory.memory = current_memory

    await db.commit()
    await db.refresh(memory)

    return memory.memory


def should_save_memory(message: str) -> bool:
    text = message.lower().strip()

    triggers = (
        "remember",
        "save this",
        "keep this in mind",
        "i prefer",
        "i like",
        "i don't like",
        "i hate",
        "from now on",
        "save in my memory",
        "store this in my memory",
        "remember this for me",
        "remember this",
    )

    return text.startswith(triggers)
