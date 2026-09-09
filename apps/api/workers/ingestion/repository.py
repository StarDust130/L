from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .extract import ExtractedJob, dedupe_key
from .models import IngestionRun, Job, JobSource
from .quality import QualityDecision
from .sources import SourceProfile


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


async def ensure_source(session: AsyncSession, profile: SourceProfile) -> JobSource:
    result = await session.execute(select(JobSource).where(JobSource.key == profile.key))
    source = result.scalar_one_or_none()
    if source:
        return source
    source = JobSource(
        key=profile.key,
        name=profile.name,
        domain=profile.domain,
        source_type=profile.source_type,
    )
    session.add(source)
    await session.flush()
    return source


async def start_run(session: AsyncSession, profile: SourceProfile) -> IngestionRun:
    run = IngestionRun(source_key=profile.key)
    session.add(run)
    await session.flush()
    return run


async def save_job(
    session: AsyncSession,
    profile: SourceProfile,
    extracted: ExtractedJob,
    decision: QualityDecision,
) -> bool:
    key = dedupe_key(extracted)
    result = await session.execute(select(Job).where(Job.dedupe_key == key))
    existing = result.scalar_one_or_none()
    now = utc_now()

    if existing:
        existing.last_seen_at = now
        existing.updated_at = now
        if decision.score > existing.quality_score:
            existing.quality_score = decision.score
            existing.evidence = extracted.evidence
        if extracted.description and len(extracted.description) > len(existing.description or ""):
            existing.description = extracted.description
        return False

    session.add(
        Job(
            source_key=profile.key,
            external_id=extracted.external_id,
            canonical_url=extracted.canonical_url,
            apply_url=extracted.apply_url,
            dedupe_key=key,
            title=extracted.title,
            company_name=extracted.company_name,
            description=extracted.description,
            location_text=extracted.location_text,
            locations=extracted.locations,
            remote=extracted.remote,
            remote_scope=extracted.remote_scope,
            eligible_countries=extracted.eligible_countries,
            job_category=decision.category,
            employment_type=extracted.employment_type,
            salary_text=extracted.salary_text,
            posted_at=extracted.posted_at,
            quality_score=decision.score,
            extraction_confidence=extracted.extraction_confidence,
            eligibility_confidence=decision.eligibility_confidence,
            status="active",
            extraction_method=extracted.method,
            evidence={**extracted.evidence, "quality_reason": decision.reason},
            first_seen_at=now,
            last_seen_at=now,
        )
    )
    return True
