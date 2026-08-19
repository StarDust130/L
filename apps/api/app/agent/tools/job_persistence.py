import hashlib
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.jobs import DiscoveredJob
from app.company.company_model import Company
from app.job.job_model import Job


def _normalize_url(url: str | None) -> str:
    """
    Normalize a URL for identity comparison.
    """

    if not url:
        return ""

    url = url.strip()

    if not url:
        return ""

    parsed = urlsplit(url)

    return urlunsplit(
        (
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/") or "/" if parsed.path else "",
            parsed.query,
            "",
        )
    ).lower()


def make_job_fingerprint(
    job: DiscoveredJob,
) -> str:
    """
    Create a stable fallback identity for a discovered job.

    Prefer:
        company + title + location

    Apply URL is NOT used here because it may be missing on the
    first discovery and appear later.
    """

    company = (job.get("company") or "").strip().casefold()

    title = (job.get("title") or "").strip().casefold()

    location = (job.get("location") or "").strip().casefold()

    identity = f"{company}|{title}|{location}"

    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


async def _find_existing_job(
    db: AsyncSession,
    job_data: DiscoveredJob,
    source: str,
    company_id: int,
) -> Job | None:
    """
    Find an existing job using the safest identity available.

    Priority:
        1. apply_url
        2. fallback fingerprint
        3. source + company + title + location
    """

    apply_url = _normalize_url(job_data.get("apply_url"))

    fingerprint = make_job_fingerprint(job_data)

    # 1️⃣ Exact application URL.
    if apply_url:
        result = await db.execute(
            select(Job).where(
                func.lower(Job.apply_url) == apply_url,
            )
        )

        existing = result.scalar_one_or_none()

        if existing is not None:
            return existing

    # 2️⃣ Stable fallback fingerprint.
    result = await db.execute(
        select(Job).where(
            Job.fingerprint == fingerprint,
        )
    )

    existing = result.scalar_one_or_none()

    if existing is not None:
        return existing

    # 3️⃣ Same source + company + normalized title/location.
    title = (job_data.get("title") or "").strip()

    location = (job_data.get("location") or "").strip()

    result = await db.execute(
        select(Job).where(
            Job.source == source,
            Job.company_id == company_id,
            func.lower(Job.title) == title.casefold(),
            func.lower(Job.location) == location.casefold(),
        )
    )

    return result.scalar_one_or_none()


async def save_discovered_job(
    db: AsyncSession,
    job_data: DiscoveredJob,
    source: str,
) -> bool:
    """
    Save a new job or update an existing job.

    Returns:
        True  -> inserted or updated
        False -> already existed with no changes
    """

    title = (job_data.get("title") or "").strip()

    company_name = (job_data.get("company") or "").strip()

    location = (job_data.get("location") or "").strip() or None

    description = (job_data.get("description") or "").strip() or None

    salary = (job_data.get("salary") or "").strip() or None

    apply_url = (job_data.get("apply_url") or "").strip() or None

    company_website = (job_data.get("company_website") or "").strip() or None

    if not title or not company_name:
        return False

    fingerprint = make_job_fingerprint(job_data)

    # ---------------------------------------------------------
    # 1️⃣ Find company.
    # ---------------------------------------------------------

    result = await db.execute(
        select(Company).where(func.lower(Company.name) == company_name.casefold())
    )

    company = result.scalar_one_or_none()

    if company is None:
        company = Company(
            name=company_name,
            website=company_website,
            source=source,
            is_hiring=True,
        )

        db.add(company)

        await db.flush()

    else:
        # Fill missing company information.
        if not company.website and company_website:
            company.website = company_website

        if not company.source:
            company.source = source

        company.is_hiring = True

    # ---------------------------------------------------------
    # 2️⃣ Find existing job.
    # ---------------------------------------------------------

    existing = await _find_existing_job(
        db=db,
        job_data=job_data,
        source=source,
        company_id=company.id,
    )

    # ---------------------------------------------------------
    # 3️⃣ Existing job → update.
    # ---------------------------------------------------------

    if existing is not None:
        changed = False

        # Update title only when useful.
        if title and existing.title != title:
            existing.title = title
            changed = True

        # Fill missing location.
        if location and existing.location != location:
            existing.location = location
            changed = True

        # Prefer real description over empty/weak value.
        if description:
            if not existing.description or len(description) > len(existing.description):
                existing.description = description
                changed = True

        # Fill/update salary.
        if salary and existing.salary != salary:
            existing.salary = salary
            changed = True

        # Fill application URL.
        if apply_url:
            normalized_existing_url = _normalize_url(existing.apply_url)

            normalized_new_url = _normalize_url(apply_url)

            if normalized_existing_url != normalized_new_url:
                existing.apply_url = apply_url
                changed = True

        # Update source if missing.
        if not existing.source:
            existing.source = source
            changed = True

        # Keep fingerprint current.
        if existing.fingerprint != fingerprint:
            existing.fingerprint = fingerprint
            changed = True

        if changed:
            await db.flush()

            return True

        return False

    # ---------------------------------------------------------
    # 4️⃣ New job → insert.
    # ---------------------------------------------------------

    new_job = Job(
        external_id=None,
        title=title,
        location=location,
        description=description,
        salary=salary,
        apply_url=apply_url,
        source=source,
        company_id=company.id,
        fingerprint=fingerprint,
    )

    db.add(new_job)

    await db.flush()

    return True
