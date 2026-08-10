from app.db.db import get_db
from app.job.job_model import Job
from app.job.job_service import collect_and_save_jobs
from app.job.matching.ai_matching_service import calculate_compatibility_score
from app.job.matching.matching_service import match_jobs_for_user
from app.profile.profile_model import CandidateProfileRecord
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# 💼 Job API routes
router = APIRouter(prefix="/jobs", tags=["Jobs"])


# 🔎 Collect new jobs
@router.post("/collect")
async def collect_jobs(db: AsyncSession = Depends(get_db)):
    # 🔎 Collect and save jobs
    saved_count = await collect_and_save_jobs(db)

    return {
        "saved": saved_count,
    }


# 🤖 Test AI on one job #TODO: REMOVE IT LATER
@router.post("/test-ai/{job_id}")
async def test_ai_matching(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Test AI matching against one real job."""

    # 👤 Get candidate
    profile_result = await db.execute(select(CandidateProfileRecord).limit(1))

    profile = profile_result.scalar_one_or_none()

    # ❌ No candidate
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="No candidate profile found",
        )

    # 💼 Get job
    job_result = await db.execute(select(Job).where(Job.id == job_id))

    job = job_result.scalar_one_or_none()

    # ❌ No job
    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    # 🤖 Ask AI for score
    result = await calculate_compatibility_score(
        profile.profile,
        job,
    )

    # 📊 Return score
    return {
        "job_id": job.id,
        "title": job.title,
        "score": result.score,
    }


# 🧠 Match jobs for candidate
@router.post("/match")
async def match_jobs(
    db: AsyncSession = Depends(get_db),
):
    """Test the full job matching pipeline."""

    # 👤 Get candidate
    result = await db.execute(select(CandidateProfileRecord).limit(1))

    profile = result.scalar_one_or_none()

    # ❌ No candidate
    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="No candidate profile found",
        )

    # 🧠 Run job matching
    saved_count = await match_jobs_for_user(
        db=db,
        profile=profile,
    )

    # 📦 Return count
    return {
        "recommendations_created": saved_count,
    }
