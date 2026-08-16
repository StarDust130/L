import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.agent import run_agent

logger = logging.getLogger(__name__)


SOURCE_DISCOVERY_PROMPT = """
Find high-quality web sources that L can use to discover
technology companies and engineering jobs.

Focus on:
- early-stage startups
- AI companies
- software companies
- engineering jobs
- remote opportunities
- company career pages
- startup hiring platforms

Search the web.

Investigate promising results with fetch_page.

Save only sources that are genuinely useful for future
job/company discovery.

Do not save ordinary job-search articles or generic SEO pages.

Your job is to improve L's future discovery capabilities.
"""


async def discover_sources(
    db: AsyncSession,
    user_id: str,
) -> str:
    """
    🔎 Run one source-discovery cycle.

    The agent decides:
        search → inspect → save
    """

    logger.info("🔎 source_discovery_started")

    result = await run_agent(
        db=db,
        message=SOURCE_DISCOVERY_PROMPT,
        user_id=user_id,
    )

    logger.info("🔎 source_discovery_finished")

    return result