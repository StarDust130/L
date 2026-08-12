from app.job.job_model import Job
from app.job.recommendation_model import Recommendation
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_my_recommendations(
    db: AsyncSession,
    user_id: str,
) -> list[dict[str, object]]:
    """💼 Get the user's best job recommendations."""

    result = await db.execute(
        select(
            Job.id,
            Job.title,
            Job.company_id,
            Job.location,
            Job.apply_url,
            Recommendation.match_score,
        )
        .join(
            Recommendation,
            Recommendation.job_id == Job.id,
        )
        .where(
            Recommendation.clerk_user_id == user_id,
        )
        .order_by(
            Recommendation.match_score.desc(),
        )
        .limit(10)
    )

    rows = result.all()

    return [
        {
            "job_id": row.id,
            "title": row.title,
            "company_id": row.company_id,
            "location": row.location,
            "apply_url": row.apply_url,
            "match_score": row.match_score,
        }
        for row in rows
    ]
