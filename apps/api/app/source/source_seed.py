from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.source.source_model import Source

KNOWN_SOURCES = [
    {
        "name": "Y Combinator Companies",
        "url": "https://www.ycombinator.com/companies",
        "source_type": "company_directory",
        "description": "Startup directory containing YC companies.",
    },
    {
        "name": "Wellfound",
        "url": "https://wellfound.com/jobs",
        "source_type": "job_board",
        "description": "Startup-focused job marketplace.",
    },
    {
        "name": "Startup Jobs",
        "url": "https://startup.jobs",
        "source_type": "job_board",
        "description": "Startup-focused job listings.",
    },
]


async def seed_sources(db: AsyncSession) -> None:
    """🌱 Add our initial trusted sources once."""

    for data in KNOWN_SOURCES:
        result = await db.execute(
            select(Source).where(
                Source.url == data["url"],
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            continue

        db.add(Source(**data))

    await db.commit()
