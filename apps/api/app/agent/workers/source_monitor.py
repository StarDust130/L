import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.extract import extract_jobs_from_page
from app.agent.tools.web import fetch_page
from app.source.source_model import Source

logger = logging.getLogger(__name__)


async def monitor_sources(
    db: AsyncSession,
) -> dict[str, int]:
    """🔄 Check known sources for new job listings."""

    result = await db.execute(
        select(Source).order_by(
            Source.quality_score.desc(),
        )
    )

    sources = result.scalars().all()

    checked = 0
    failed = 0
    jobs_found = 0

    for source in sources:
        try:
            logger.info(
                "🔄 source_check_started source=%s",
                source.name,
            )

            # 🌐 Read the current source page.
            page_text = await fetch_page(
                source.url,
            )

            if page_text.startswith("PAGE_FETCH_FAILED:"):
                source.failure_count += 1
                failed += 1
                continue

            # 🧠 Extract actual job listings.
            jobs = await extract_jobs_from_page(page_text)

            jobs_found += len(jobs)

            # 🕐 Update source state.
            source.last_checked = datetime.now(UTC)
            source.failure_count = 0

            checked += 1

            logger.info(
                "🔄 source_check_completed source=%s jobs=%s",
                source.name,
                len(jobs),
            )

        except Exception:
            logger.exception(
                "❌ source_check_failed source=%s",
                source.name,
            )

            source.failure_count += 1
            failed += 1

    await db.commit()

    return {
        "sources_checked": checked,
        "sources_failed": failed,
        "jobs_found": jobs_found,
    }
