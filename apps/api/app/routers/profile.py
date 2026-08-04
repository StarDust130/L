from typing import Annotated

from fastapi import APIRouter, Depends

from app.auth import require_user
from app.schemas.profile import (
    CandidateProfile,
    ProfileExtractionRequest,
)
from app.services.profile_ai import extract_candidate_profile

router = APIRouter(
    prefix="/api/profile",
    tags=["profile"],
)


@router.post("/extract", response_model=CandidateProfile)
async def extract_profile(
    payload: ProfileExtractionRequest,
    _user_id: Annotated[str, Depends(require_user)],
) -> CandidateProfile:
    # 🧠 Convert resume text into a structured profile
    return extract_candidate_profile(payload.resume_text)
