"""
RemoteOK collector ✅
       ↓
raw jobs ✅
       ↓
remove duplicates / normalize ✅
       ↓
save fresh jobs ✅
       ↓
SQLite ✅

Later we'll add:

retry
deduplication
30-day expiration
multiple sources
"""
# TODO: better deduplication two differnt source can't have same job role from same company with same title and location but different apply_url.

from app.job.collectors.remoteok_collector import remoteok_job_collector
from app.job.job_model import Job
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def collect_and_save_jobs(db: AsyncSession) -> int:
    """Collect jobs from RemoteOK and save new jobs to the database."""

    # 🌐 Get raw jobs from RemoteOK.
    raw_jobs = await remoteok_job_collector()

    saved_count = 0

    for raw_job in raw_jobs:
        external_id = str(raw_job["id"])

        # 🔎 Check if this job already exists.
        result = await db.execute(
            select(Job).where(
                Job.source == "remoteok",
                Job.external_id == external_id,
            )
        )

        existing_job = result.scalar_one_or_none()

        # ⏭️ Skip jobs we already have.
        if existing_job:
            continue

        # 🧹 Convert RemoteOK data into our Job model.
        job = Job(
            external_id=external_id,
            title=raw_job["position"],
            company=raw_job["company"],
            location=raw_job.get("location"),
            description=raw_job.get("description"),
            salary=raw_job.get("salary"),
            apply_url=raw_job["apply_url"],
            source="remoteok",
        )

        # 💾 Add the new job to the current session.
        db.add(job)

        saved_count += 1

    # ✅ Save all new jobs in one transaction.
    await db.commit()

    return saved_count
