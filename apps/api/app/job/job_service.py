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

import hashlib
import logging

from app.job.collectors.remoteok_collector import remoteok_job_collector
from app.job.job_model import Job
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


import logging

from app.company.company_model import Company

logger = logging.getLogger(__name__)


def create_job_fingerprint(
    company: str,
    title: str,
    location: str | None,
) -> str:
    """Create a stable identity for a job."""

    value = "|".join(
        [
            company.strip().lower(),
            title.strip().lower(),
            (location or "").strip().lower(),
        ]
    )

    return hashlib.sha256(value.encode()).hexdigest()


async def collect_and_save_jobs(db: AsyncSession) -> int:
    """Collect jobs from RemoteOK and save new jobs."""

    logger.info("🔎 job_collection_started")

    raw_jobs = await remoteok_job_collector()

    logger.info("📦 jobs_fetched count=%s", len(raw_jobs))

    saved_count = 0
    skipped_count = 0

    for raw_job in raw_jobs:
        external_id = str(raw_job["id"])
        company_name = raw_job["company"]

        # 🧬 Create identity for cross-source duplicate detection.
        fingerprint = create_job_fingerprint(
            company_name,
            raw_job["position"],
            raw_job.get("location"),
        )
        # 🔎 Check if another source already has this job.
        result = await db.execute(select(Job).where(Job.fingerprint == fingerprint))

        if result.scalar_one_or_none():
            skipped_count += 1
            continue

        # 🔎 Check if this job already exists.
        result = await db.execute(
            select(Job).where(
                Job.source == "remoteok",
                Job.external_id == external_id,
            )
        )

        if result.scalar_one_or_none():
            skipped_count += 1
            continue

        # 🏢 Find the company.
        company_result = await db.execute(
            select(Company).where(
                Company.name == company_name,
            )
        )

        company = company_result.scalar_one_or_none()

        # ➕ Create company if we don't have it.
        if company is None:
            company = Company(
                name=company_name,
                source="remoteok",
                external_id=str(raw_job.get("company_id"))
                if raw_job.get("company_id")
                else None,
            )

            db.add(company)

            # 🆔 Get the new company's database ID.
            await db.flush()

        # 💼 Create our normalized Job.
        job = Job(
            external_id=external_id,
            fingerprint=fingerprint,
            title=raw_job["position"],
            company_id=company.id,
            location=raw_job.get("location"),
            description=raw_job.get("description"),
            salary=raw_job.get("salary"),
            apply_url=raw_job["apply_url"],
            source="remoteok",
        )

        db.add(job)
        saved_count += 1

    # 💾 Save everything in one transaction.
    await db.commit()

    logger.info(
        "✅ job_collection_completed fetched=%s saved=%s skipped=%s",
        len(raw_jobs),
        saved_count,
        skipped_count,
    )

    return saved_count
