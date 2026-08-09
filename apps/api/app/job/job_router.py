from app.db.db import get_db
from app.job.job_service import collect_and_save_jobs
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/collect")
async def collect_jobs(db: AsyncSession = Depends(get_db)):
    # 🔎 Collect and save new jobs.
    saved_count = await collect_and_save_jobs(db)

    return {
        "saved": saved_count,
    }
