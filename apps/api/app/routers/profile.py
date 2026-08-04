from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import require_user
from app.db import get_db
from app.schemas.profile import (
    CandidateProfile,
    ProfileExtractionRequest,
)
from app.services.profile_ai import extract_candidate_profile
from app.services.profile_store import (
    get_saved_profile,
    save_profile,
)

router = APIRouter(
    prefix="/api/profile",
    tags=["profile"],
)


@router.post("/extract", response_model=CandidateProfile)
def extract_profile(
    payload: ProfileExtractionRequest,
    _user_id: Annotated[str, Depends(require_user)],
) -> CandidateProfile:
    # 🤖 Extract profile information with Groq
    return extract_candidate_profile(payload.resume_text)


@router.get("", response_model=CandidateProfile | None)
async def read_profile(
    user_id: Annotated[str, Depends(require_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CandidateProfile | None:
    # 📖 Load the signed-in user's profile
    return await get_saved_profile(session, user_id)


@router.put("", response_model=CandidateProfile)
async def update_profile(
    profile: CandidateProfile,
    user_id: Annotated[str, Depends(require_user)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CandidateProfile:
    # 💾 Save the reviewed profile
    return await save_profile(session, user_id, profile)
