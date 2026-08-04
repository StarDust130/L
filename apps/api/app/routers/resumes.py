from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile

from app.auth import require_user
from app.schemas.resume import ExtractedResume
from app.services.resume_parser import extract_resume_text

router = APIRouter(
    prefix="/api/resumes",
    tags=["resumes"],
)


@router.post(
    "/extract",
    response_model=ExtractedResume,
)
async def extract_resume(
    file: Annotated[UploadFile, File(...)],
    _user_id: Annotated[str, Depends(require_user)],
) -> ExtractedResume:
    return await extract_resume_text(file)
