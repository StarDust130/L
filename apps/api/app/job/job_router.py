from app.db.db import get_db
from app.job.job_model import Job
from app.job.job_service import collect_and_save_jobs
from app.job.matching.ai_matching_service import calculate_compatibility_score
from app.job.matching.matching_service import match_jobs_for_user
from app.profile.profile_model import CandidateProfileRecord
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/collect")
async def collect_jobs(db: AsyncSession = Depends(get_db)):
    # 🔎 Collect and save new jobs.
    saved_count = await collect_and_save_jobs(db)

    return {
        "saved": saved_count,
    }


@router.post("/test-ai/{job_id}")
async def test_ai_matching(
    job_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Test AI matching against one real job."""

    # 👤 Get one candidate profile.
    profile_result = await db.execute(select(CandidateProfileRecord).limit(1))

    profile = profile_result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="No candidate profile found",
        )

    # 💼 Get the requested job.
    job_result = await db.execute(select(Job).where(Job.id == job_id))

    job = job_result.scalar_one_or_none()

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    # 🤖 Ask AI to score the job.
    result = await calculate_compatibility_score(
        profile.profile,
        job,
    )

    return {
        "job_id": job.id,
        "title": job.title,
        "score": result.score,
    }


@router.post("/match")
async def match_jobs(
    db: AsyncSession = Depends(get_db),
):
    """Test the full job matching pipeline."""

    # 👤 Get one test profile.
    result = await db.execute(select(CandidateProfileRecord).limit(1))

    profile = result.scalar_one_or_none()

    if profile is None:
        raise HTTPException(
            status_code=404,
            detail="No candidate profile found",
        )

    # 🧠 Match all jobs for this user.
    saved_count = await match_jobs_for_user(
        db=db,
        profile=profile,
    )

    return {
        "recommendations_created": saved_count,
    }
