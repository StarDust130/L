from typing import Annotated

from app.core.auth import require_user
from app.resume.resume_schema import ExtractedResume
from app.resume.services.resume_parser import extract_resume_text
from fastapi import APIRouter, Depends, File, UploadFile

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
