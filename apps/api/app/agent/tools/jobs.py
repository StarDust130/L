from app.job.job_model import Job
from app.recommendation.recommendation_model import Recommendation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_my_recommendations(
    db: AsyncSession,
    user_id: str,
) -> list[Job]:
    """💼 Get jobs recommended for the current user."""

    result = await db.execute(
        select(Job)
        .join(
            Recommendation,
            Recommendation.job_id == Job.id,
        )
        .where(
            Recommendation.clerk_user_id == user_id,
        )
        .order_by(
            Recommendation.score.desc(),
        )
        .limit(10)
    )

    return list(result.scalars().all())
