import hashlib
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.jobs import DiscoveredJob
from app.company.company_model import Company
from app.job.job_model import Job


def make_job_fingerprint(
    job: DiscoveredJob,
) -> str:
    """🔑 Create a stable identity for a discovered job."""

    company = (job.get("company") or "").strip().lower()
    title = (job.get("title") or "").strip().lower()
    raw_apply_url = (job.get("apply_url") or "").strip()
    parsed_url = urlsplit(raw_apply_url)
    apply_url = urlunsplit(
        (
            parsed_url.scheme.lower(),
            parsed_url.netloc.lower(),
            parsed_url.path.rstrip("/") or "/" if parsed_url.path else "",
            parsed_url.query,
            "",
        )
    ).lower()

    identity = f"{company}|{title}|{apply_url}"

    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


async def save_discovered_job(
    db: AsyncSession,
    job_data: DiscoveredJob,
    source: str,
) -> bool:
    """💾 Save a job if it does not already exist."""

    apply_url = (job_data.get("apply_url") or "").strip() or None

    company_name = (job_data.get("company") or "").strip()
    fingerprint = make_job_fingerprint(job_data)

    result = await db.execute(
        select(Job).where(Job.fingerprint == fingerprint)
    )
    if result.scalar_one_or_none() is not None:
        return False

    # Find or create company.
    result = await db.execute(
        select(Company).where(func.lower(Company.name) == company_name.casefold())
    )

    company = result.scalar_one_or_none()

    if company is None:
        company = Company(name=company_name)
        db.add(company)
        await db.flush()

    # Save new job.
    db.add(
        Job(
            external_id=None,
            title=job_data["title"].strip(),
            location=job_data.get("location"),
            description=job_data.get("description"),
            salary=job_data.get("salary"),
            apply_url=apply_url or None,
            source=source,
            company_id=company.id,
            fingerprint=fingerprint,
        )
    )
    await db.flush()

    return True
