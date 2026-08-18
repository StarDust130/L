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
    """Return the best known job/company sources."""

    result = await db.execute(
        select(Source)
        .order_by(
            Source.quality_score.desc(),
            Source.last_checked.asc(),
        )
        .limit(20)
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


async def save_source(
    db: AsyncSession,
    name: str,
    url: str,
    source_type: str,
    description: str | None = None,
) -> SourceResult:
    """
    💾 Save a useful discovery source.

    We check the URL first so L cannot create duplicate sources.
    """

    result = await db.execute(select(Source).where(Source.url == url))

    existing = result.scalar_one_or_none()

    # ♻️ Source already exists.
    if existing:
        return {
            "id": existing.id,
            "name": existing.name,
            "url": existing.url,
            "source_type": existing.source_type,
            "quality_score": existing.quality_score,
        }

    source = Source(
        name=name,
        url=url,
        source_type=source_type,
        description=description,
        quality_score=0.0,
    )

    db.add(source)

    await db.commit()
    await db.refresh(source)

    return {
        "id": source.id,
        "name": source.name,
        "url": source.url,
        "source_type": source.source_type,
        "quality_score": source.quality_score,
    }
