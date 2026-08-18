from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.memory.memory_model import UserMemory
from app.profile.profile_model import CandidateProfileRecord


async def build_user_context(
    db: AsyncSession,
    user_id: str,
) -> dict[str, Any]:
    """
    Build the user's context for the agent.

    Combines:
    - Candidate profile from resume
    - Long-term memory from conversations
    """

    # Get resume/profile
    profile_result = await db.execute(
        select(CandidateProfileRecord).where(
            CandidateProfileRecord.clerk_user_id == user_id,
        )
    )

    profile = profile_result.scalar_one_or_none()

    # Get long-term memory
    memory_result = await db.execute(
        select(UserMemory).where(
            UserMemory.clerk_user_id == user_id,
        )
    )

    memory = memory_result.scalar_one_or_none()

    return {
        "profile": profile.profile if profile else {},
        "memory": memory.memory if memory else {},
    }
