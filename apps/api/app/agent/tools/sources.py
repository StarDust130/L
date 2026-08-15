from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.source.source_model import Source


class SourceResult(TypedDict):
    """🌐 Small source representation returned to L."""

    id: int
    name: str
    url: str
    source_type: str
    quality_score: float


async def get_known_sources(
    db: AsyncSession,
) -> list[SourceResult]:
    """Return the sources L already knows about."""

    result = await db.execute(
        select(Source).order_by(
            Source.quality_score.desc(),
        )
    )

    sources = result.scalars().all()

    return [
        {
            "id": source.id,
            "name": source.name,
            "url": source.url,
            "source_type": source.source_type,
            "quality_score": source.quality_score,
        }
        for source in sources
    ]
