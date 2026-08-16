import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.extract import extract_jobs_from_page
from app.agent.tools.job_persistence import save_discovered_job
from app.agent.tools.job_validation import validate_job
from app.agent.tools.jobs import normalize_discovered_job
from app.agent.tools.web import fetch_page
from app.source.source_model import Source

logger = logging.getLogger(__name__)


async def monitor_sources(
    db: AsyncSession,
) -> dict[str, int]:
    """
    🔄 Check known sources and save new jobs.

    Source Monitor is responsible for:
        source → page → jobs → validate → deduplicate → save
    """

    result = await db.execute(
        select(Source).order_by(
            Source.quality_score.desc(),
        )
    )

    sources = result.scalars().all()

    sources_checked = 0
    sources_failed = 0
    jobs_found = 0
    invalid_jobs = 0
    duplicate_jobs = 0
    new_jobs_saved = 0

    for source in sources:
        logger.info(
            "🔄 source_check_started source=%s",
            source.name,
        )

        try:
            # 🌐 Read the source.
            page_text = await fetch_page(source.url)

            # 🚫 Source could not be fetched.
            if page_text.startswith("PAGE_FETCH_FAILED:"):
                source.failure_count += 1
                sources_failed += 1

                logger.warning(
                    "⚠️ source_fetch_failed source=%s failures=%s",
                    source.name,
                    source.failure_count,
                )

                continue

            # 🧠 Extract job listings.
            jobs = await extract_jobs_from_page(page_text, source.url)

            jobs_found += len(jobs)

            # 💾 Validate + deduplicate + save.
            for raw_job in jobs:
                try:
                    job = normalize_discovered_job(raw_job, source.url)
                    if job is None:
                        invalid_jobs += 1
                        logger.warning(
                            "invalid_job source=%s reason=invalid_job_shape",
                            source.name,
                        )
                        continue

                    reason = validate_job(job)
                except Exception:
                    invalid_jobs += 1
                    logger.exception(
                        "job_processing_failed source=%s title=%s",
                        source.name,
                        getattr(raw_job, "get", lambda _key: None)("title"),
                    )
                    continue

                if reason:
                    invalid_jobs += 1

                    logger.warning(
                        "⚠️ invalid_job source=%s reason=%s title=%s",
                        source.name,
                        reason,
                        job.get("title"),
                    )

                    continue

                try:
                    async with db.begin_nested():
                        saved = await save_discovered_job(
                            db=db,
                            job_data=job,
                            source=source.name,
                        )

                    if saved:
                        new_jobs_saved += 1
                    else:
                        duplicate_jobs += 1

                except Exception:
                    logger.exception(
                        "❌ job_save_failed source=%s title=%s",
                        source.name,
                        job.get("title"),
                    )

                    # 🛡️ One bad job must not stop the rest.
                    continue

            # ✅ Source successfully checked.
            source.last_checked = datetime.now(UTC)
            source.failure_count = 0

            sources_checked += 1

            logger.info(
                "🔄 source_check_completed source=%s jobs=%s",
                source.name,
                len(jobs),
            )

        except Exception:
            # 🛡️ One broken source must never stop all other sources.
            logger.exception(
                "❌ source_check_failed source=%s",
                source.name,
            )

            source.failure_count += 1
            sources_failed += 1

    # 💾 Commit all source/job changes together.
    await db.commit()

    logger.info(
        "✅ source_monitor_completed checked=%s failed=%s "
        "found=%s invalid=%s duplicates=%s new=%s",
        sources_checked,
        sources_failed,
        jobs_found,
        invalid_jobs,
        duplicate_jobs,
        new_jobs_saved,
    )

    return {
        "sources_checked": sources_checked,
        "sources_failed": sources_failed,
        "jobs_found": jobs_found,
        "invalid_jobs": invalid_jobs,
        "duplicate_jobs": duplicate_jobs,
        "new_jobs_saved": new_jobs_saved,
    }
