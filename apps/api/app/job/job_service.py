"""
RemoteOK collector ✅
       ↓
raw jobs 📦
       ↓
remove duplicates / normalize 🧹
       ↓
save fresh jobs 💾
       ↓
SQLite 🗄️

Later we'll add:
retry 🔄
deduplication 🧬
30-day expiration 📅
multiple sources 🌐
"""

# TODO: 🧬 Improve deduplication.
# Different sources can have the same company, role, title, and location
# but different apply URLs.

import hashlib  # 🔐 Create job fingerprints
import logging  # 📝 Write application logs

from app.company.company_model import Company  # 🏢 Company database model
from app.job.collectors.remoteok_collector import (
    remoteok_job_collector,  # 📥 Get jobs from RemoteOK
)
from app.job.job_model import Job  # 💼 Job database model
from sqlalchemy import select  # 🔎 Build database queries
from sqlalchemy.ext.asyncio import AsyncSession  # 🔄 Async database session

# 📝 Create a logger for this file
logger = logging.getLogger(__name__)


# 🧬 Create a unique fingerprint for a job
def create_job_fingerprint(
    company: str,
    title: str,
    location: str | None,
) -> str:
    # 🧹 Clean company, title, and location
    value = "|".join(
        [
            company.strip().lower(),
            title.strip().lower(),
            (location or "").strip().lower(),
        ]
    )

    # 🔐 Create a stable SHA-256 fingerprint
    return hashlib.sha256(value.encode()).hexdigest()


# 📥 Collect jobs from RemoteOK and save new jobs
async def collect_and_save_jobs(db: AsyncSession) -> int:
    # 🚀 Start job collection
    logger.info("🔎 job_collection_started")

    # 📥 Get raw jobs from RemoteOK
    raw_jobs = await remoteok_job_collector()

    # 📊 Log how many jobs were fetched
    logger.info("📦 jobs_fetched count=%s", len(raw_jobs))

    # 📊 Track saved and skipped jobs
    saved_count = 0
    skipped_count = 0

    # 🔄 Process every job
    for raw_job in raw_jobs:
        # 🆔 Get RemoteOK job ID
        external_id = str(raw_job["id"])

        # 🏢 Get company name
        company_name = raw_job["company"]

        # 🧬 Create fingerprint for duplicate detection
        fingerprint = create_job_fingerprint(
            company_name,
            raw_job["position"],
            raw_job.get("location"),
        )

        # 🔎 Check if another source already has this job
        result = await db.execute(
            select(Job).where(
                Job.fingerprint == fingerprint,
            )
        )

        # ⏭️ Skip duplicate job
        if result.scalar_one_or_none():
            skipped_count += 1
            continue

        # 🔎 Check if this RemoteOK job already exists
        result = await db.execute(
            select(Job).where(
                Job.source == "remoteok",
                Job.external_id == external_id,
            )
        )

        # ⏭️ Skip existing job
        if result.scalar_one_or_none():
            skipped_count += 1
            continue

        # 🏢 Find existing company
        company_result = await db.execute(
            select(Company).where(
                Company.name == company_name,
            )
        )

        # 📦 Get company or None
        company = company_result.scalar_one_or_none()

        # ➕ Create company if it doesn't exist
        if company is None:
            company = Company(
                name=company_name,
                source="remoteok",
                external_id=(
                    str(raw_job.get("company_id"))
                    if raw_job.get("company_id")
                    else None
                ),
            )

            # 📦 Add company to database
            db.add(company)

            # 🆔 Generate company database ID
            await db.flush()

        # 💼 Create normalized Job
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

        # 📦 Add job to database
        db.add(job)

        # 📈 Increase saved job count
        saved_count += 1

    # 💾 Save all changes in one transaction
    await db.commit()

    # ✅ Log collection results
    logger.info(
        "✅ job_collection_completed fetched=%s saved=%s skipped=%s",
        len(raw_jobs),
        saved_count,
        skipped_count,
    )

    # 📤 Return number of saved jobs
    return saved_count
