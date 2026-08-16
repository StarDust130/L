from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.company.collectors.yc_company_discovery import (
    discover_yc_companies,
)
from app.company.company_model import Company


async def discover_and_save_yc_companies(
    db: AsyncSession,
) -> int:
    """🔎 Discover YC companies and save new companies."""

    companies = await discover_yc_companies()

    saved_count = 0

    for company_data in companies:
        # 🔎 Check whether this YC company already exists.
        result = await db.execute(
            select(Company).where(
                Company.source == "yc",
                Company.external_id == company_data.yc_url,
            )
        )

        existing = result.scalar_one_or_none()

        if existing:
            continue

        # 💾 Save the company.
        db.add(
            Company(
                name=company_data.name,
                website=company_data.yc_url,
                source="yc",
                external_id=company_data.yc_url,
            )
        )

        saved_count += 1

    await db.commit()

    return saved_count
