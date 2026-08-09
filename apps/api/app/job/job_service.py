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

import logging

from app.job.collectors.remoteok_collector import remoteok_job_collector
from app.job.job_model import Job
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def collect_and_save_jobs(db: AsyncSession) -> int:
    """Collect jobs from RemoteOK and save new jobs."""

    logger.info(" 🕒 job_collection_started")

    # 🌐 Get raw jobs from RemoteOK.
    raw_jobs = await remoteok_job_collector()

    logger.info("💁 jobs_fetched count=%s", len(raw_jobs))

    saved_count = 0
    skipped_count = 0

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

        # ⏭️ Skip existing jobs.
        if existing_job:
            skipped_count += 1
            continue

        # 🧹 Convert source data into our Job model.
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

        # 💾 Add the new job to the session.
        db.add(job)

        saved_count += 1

    # ✅ Save all new jobs in one transaction.
    await db.commit()

    logger.info(
        "✅ job_collection_completed fetched=%s saved=%s skipped=%s",
        len(raw_jobs),
        saved_count,
        skipped_count,
    )

    return saved_count
