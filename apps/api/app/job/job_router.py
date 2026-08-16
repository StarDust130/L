from fastapi import APIRouter, Depends, HTTPException  # 🚀 FastAPI tools
from sqlalchemy import select  # 🔍 Build database queries
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 Async DB session

from app.agent.agent import run_agent  # 👤 Profile model
from app.agent.tools.jobs import get_my_recommendations
from app.agent.tools.web import search_web
from app.agent.workers.source_discovery import discover_sources
from app.agent.workers.source_monitor import monitor_sources
from app.db.db import get_db  # 🗄️ Database dependency
from app.job.job_service import collect_and_save_jobs  # 📥 Collect jobs
from app.job.matching.matching_service import match_jobs_for_user  # 🧠 Match jobs
from app.profile.profile_model import CandidateProfileRecord

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


# TODO: REMOVE IT ONLY FOR TEST
@router.post("/agent/test")
async def test_agent(
    message: str,
    db: AsyncSession = Depends(get_db),
):
    response = await run_agent(
        db=db,
        message=message,
        user_id="user_3HmEkdg0OKTZkY6srwYUiK4s2YN",
    )

    return {
        "response": response,
    }


@router.get("/agent/test-recommendations")
async def test_recommendations(
    db: AsyncSession = Depends(get_db),
):
    jobs = await get_my_recommendations(
        db=db,
        user_id="user_3HmEkdg0OKTZkY6srwYUiK4s2YN",
    )

    return {
        "count": len(jobs),
        "jobs": jobs,
    }


@router.post("/agent/test-search")
async def test_search(
    query: str,
):
    results = await search_web(
        query=query,
    )

    return {
        "count": len(results),
        "results": results,
    }


@router.post("/agent/test-source-discovery")
async def test_source_discovery(
    db: AsyncSession = Depends(get_db),
):
    result = await discover_sources(
        db=db,
        user_id="source-discovery-test",
    )

    return {
        "response": result,
    }


@router.post("/agent/test-source-monitor")
async def test_source_monitor(
    db: AsyncSession = Depends(get_db),
):
    result = await monitor_sources(
        db=db,
    )

    return result
