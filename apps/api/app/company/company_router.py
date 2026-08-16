from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.company.company_service import (
    discover_and_save_yc_companies,
)
from app.db.db import get_db

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
)


@router.post("/discover/yc")
async def discover_yc(
    db: AsyncSession = Depends(get_db),
):
    """🔎 Discover YC companies."""

    saved_count = await discover_and_save_yc_companies(
        db=db,
    )

    return {
        "source": "yc",
        "saved": saved_count,
    }
