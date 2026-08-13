from datetime import UTC, datetime  # 🕐 Work with UTC time

from app.profile.profile_model import CandidateProfileRecord  # 🗄️ Database model
from app.profile.profile_schema import CandidateProfile  # 📋 Profile schema
from sqlalchemy import select  # 🔍 Build database queries
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 Async database session


# 🔎 Get a user's saved profile from the database
async def get_saved_profile(
    session: AsyncSession,
    clerk_user_id: str,
) -> CandidateProfile | None:
    # 🔍 Find this user's profile
    result = await session.execute(
        select(CandidateProfileRecord).where(
            CandidateProfileRecord.clerk_user_id == clerk_user_id
        )
    )

    # 📦 Get the profile or None
    record = result.scalar_one_or_none()

    # ❌ Return nothing if profile doesn't exist
    if record is None:
        return None

    # ✅ Convert database data into a profile
    return CandidateProfile.model_validate(record.profile)


# 💾 Save a new profile or update an existing profile
async def save_profile(
    session: AsyncSession,
    clerk_user_id: str,
    profile: CandidateProfile,
) -> CandidateProfile:
    # 🔍 Check if this user already has a profile
    result = await session.execute(
        select(CandidateProfileRecord).where(
            CandidateProfileRecord.clerk_user_id == clerk_user_id
        )
    )

    # 📦 Get existing profile or None
    record = result.scalar_one_or_none()

    # 🔄 Convert profile into JSON
    profile_data = profile.model_dump(mode="json")

    # ➕ Create a new profile if none exists
    if record is None:
        record = CandidateProfileRecord(
            clerk_user_id=clerk_user_id,
            profile=profile_data,
        )
        session.add(record)

    else:
        # ✏️ Update the existing profile
        record.profile = profile_data
        record.updated_at = datetime.now(UTC)

    # 💾 Save changes
    await session.commit()

    # 📤 Return the profile
    return profile
