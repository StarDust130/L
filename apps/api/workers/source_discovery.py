import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.agent import run_agent

logger = logging.getLogger(__name__)


SOURCE_DISCOVERY_PROMPT = """
You are running a SOURCE DISCOVERY task for L.

Your goal is to discover NEW, high-quality sources that can improve
L's future ability to find technology jobs and companies.

This is a source-discovery task, NOT a normal chat request.

WORKFLOW:

1. First call get_known_sources.
2. Study the existing sources.
3. Do NOT search for or save sources that are already known.
4. Identify gaps in L's current source coverage.
5. Search the web for NEW sources that fill those gaps.
6. Prefer sources that can repeatedly provide useful information.

LOOK FOR:

- startup engineering job boards
- Python / backend / FastAPI job sources
- AI / ML engineering job sources
- remote-first engineering sources
- niche technical communities with hiring
- startup hiring platforms
- company career directories
- early-stage startup directories
- technology company databases
- startup funding/news sources that reveal promising new companies
- sources that reveal companies before they become widely known

IMPORTANT:

A funding/news source can be valuable even when it does not contain jobs
directly, if it helps discover promising technology companies that may
become hiring targets.

Do NOT save:

- ordinary career articles
- SEO pages
- generic "top job boards" articles
- spam
- low-quality aggregators
- duplicate platforms
- random job listings
- individual jobs as sources

For every promising NEW source:

1. Inspect it with fetch_page.
2. Verify that it contains genuinely useful information.
3. Save it only if it provides reusable discovery value.

QUALITY OVER QUANTITY:

Prefer 2 excellent new sources over 10 mediocre ones.

Normally save no more than 2–5 strong sources in one discovery cycle.

Do not keep searching after enough valuable sources have been found.

IMPORTANT DISTINCTION:

You are discovering reusable SOURCES.

Example:

Good:
"YC startup jobs"

Bad:
"Backend Engineer at Company X"

Good:
"a startup funding database"

Bad:
"a single funding article"

EFFICIENCY:

Gemini requests are limited.

Use:
get_known_sources
→ a few focused searches
→ inspect strongest candidates
→ save best NEW sources
→ stop

Do not repeatedly search the same query.

Do not rediscover known sources.

Do not perform random exploration.

STOP when the current source gaps have been explored and the best NEW
sources have been inspected and saved.

Return a very short summary of what you discovered.
"""


async def discover_sources(
    db: AsyncSession,
    user_id: str,
) -> str:
    """
    Run one source-discovery cycle.

    The main L system prompt controls personality and global behavior.
    This prompt only defines the current discovery task.
    """

    logger.info(
        "🔎 source_discovery_started | user=%s",
        user_id,
    )

    result = await run_agent(
        db=db,
        message=SOURCE_DISCOVERY_PROMPT,
        user_id=user_id,
    )

    logger.info(
        "✅ source_discovery_finished | user=%s | result=%s",
        user_id,
        result.content[:500],
    )

    return result.content