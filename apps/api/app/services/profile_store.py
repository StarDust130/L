from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import CandidateProfileRecord
from app.schemas.profile import CandidateProfile


async def get_saved_profile(
    session: AsyncSession,
    clerk_user_id: str,
) -> CandidateProfile | None:
    # 🔎 Find this user's profile
    result = await session.execute(
        select(CandidateProfileRecord).where(
            CandidateProfileRecord.clerk_user_id == clerk_user_id
        )
    )

    record = result.scalar_one_or_none()

    if record is None:
        return None

    # ✅ Validate data again when reading
    return CandidateProfile.model_validate(record.profile)


async def save_profile(
    session: AsyncSession,
    clerk_user_id: str,
    profile: CandidateProfile,
) -> CandidateProfile:
    # 🔎 Check if this user already has a profile
    result = await session.execute(
        select(CandidateProfileRecord).where(
            CandidateProfileRecord.clerk_user_id == clerk_user_id
        )
    )

    record = result.scalar_one_or_none()

    # 📦 Convert Pydantic data into database-safe JSON
    profile_data = profile.model_dump(mode="json")

    if record is None:
        # ➕ Create the first profile
        record = CandidateProfileRecord(
            clerk_user_id=clerk_user_id,
            profile=profile_data,
        )
        session.add(record)
    else:
        # ✏️ Update the existing profile
        record.profile = profile_data
        record.updated_at = datetime.now(UTC)

    await session.commit()

    return profile
