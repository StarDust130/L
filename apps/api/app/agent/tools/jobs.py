from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.company.company_model import Company
from app.job.job_model import Job
from app.job.recommendation_model import Recommendation


class JobRecommendation(TypedDict):
    """The job data needed by the agent and Telegram job cards."""

    job_id: int
    title: str
    company: str
    location: str | None
    salary: str | None
    apply_url: str
    match_score: float


async def get_my_recommendations(
    db: AsyncSession,
    user_id: str,
) -> list[JobRecommendation]:
    """Return the authenticated user's ten strongest job matches."""

    result = await db.execute(
        select(
            Job.id,
            Job.title,
            Company.name,
            Job.location,
            Job.salary,
            Job.apply_url,
            Recommendation.match_score,
        )
        .join(
            Recommendation,
            Recommendation.job_id == Job.id,
        )
        .join(
            Company,
            Company.id == Job.company_id,
        )
        .where(
            Recommendation.clerk_user_id == user_id,
        )
        .order_by(
            Recommendation.match_score.desc(),
        )
        .limit(10)
    )

    rows = result.tuples().all()
    recommendations: list[JobRecommendation] = []

    for row in rows:
        job_id, title, company, location, salary, apply_url, match_score = row
        recommendations.append(
            {
                "job_id": job_id,
                "title": title,
                "company": company,
                "location": location,
                "salary": salary,
                "apply_url": apply_url,
                "match_score": float(match_score),
            }
        )

    return recommendations
