from app.db.db import get_db  # 🗄️ Database dependency
from app.job.job_service import collect_and_save_jobs  # 📥 Collect jobs
from app.job.matching.matching_service import match_jobs_for_user  # 🧠 Match jobs
from app.profile.profile_model import CandidateProfileRecord  # 👤 Profile model
from fastapi import APIRouter, Depends, HTTPException  # 🚀 FastAPI tools
from sqlalchemy import select  # 🔍 Build database queries
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 Async DB session

# 💼 Job API routes
router = APIRouter(prefix="/jobs", tags=["Jobs"])


# 📥 Collect new jobs and save them to the database
@router.post("/collect")
async def collect_jobs(db: AsyncSession = Depends(get_db)):
    # 🔎 Collect and save jobs
    saved_count = await collect_and_save_jobs(db)

    # 📤 Return number of saved jobs
    return {
        "saved": saved_count,
    }


# 🧠 Match available jobs with the candidate profile
@router.post("/match")
async def match_jobs(
    db: AsyncSession = Depends(get_db),
):
    # 👤 Find a candidate profile
    result = await db.execute(select(CandidateProfileRecord).limit(1))

    # 📦 Get the profile
    profile = result.scalar_one_or_none()

    # ❌ Stop if no profile exists
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="No candidate profile found",
        )

    # 🧠 Run the job matching process
    saved_count = await match_jobs_for_user(
        db=db,
        profile=profile,
    )

    # 📤 Return number of recommendations
    return {
        "recommendations_created": saved_count,
    }
