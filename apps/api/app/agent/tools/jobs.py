from typing import TypedDict
from urllib.parse import urljoin, urlparse

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.company.company_model import Company
from app.job.job_model import Job
from app.job.recommendation_model import Recommendation


class DiscoveredJob(TypedDict):
    """💼 Raw job data extracted from a source."""

    title: str | None
    company: str | None
    location: str | None
    salary: str | None
    description: str | None
    apply_url: str | None
    company_website: str | None
    detail_url: str | None


def normalize_discovered_job(
    raw_job: object,
    source_url: str,
) -> DiscoveredJob | None:
    """Convert one extractor result into the discovered-job contract."""
    if not isinstance(raw_job, dict):
        return None

    title = raw_job.get("title")
    company = raw_job.get("company")

    def optional_text(value: object) -> str | None:
        if not isinstance(value, str):
            return None
        value = value.strip()
        return value or None

    apply_url = optional_text(raw_job.get("apply_url"))
    if apply_url:
        parsed_apply_url = urlparse(apply_url)
        if parsed_apply_url.scheme in {
            "",
            "http",
            "https",
        } and not apply_url.startswith("#"):
            apply_url = urljoin(source_url, apply_url)

    detail_url = optional_text(raw_job.get("detail_url"))
    if detail_url:
        parsed_detail_url = urlparse(detail_url)
        if parsed_detail_url.scheme in {
            "",
            "http",
            "https",
        } and not detail_url.startswith("#"):
            detail_url = urljoin(source_url, detail_url)
        else:
            detail_url = None

    company_website = optional_text(raw_job.get("company_website"))
    if company_website:
        parsed_company_website = urlparse(company_website)
        if parsed_company_website.scheme in {
            "",
            "http",
            "https",
        } and not company_website.startswith("#"):
            company_website = urljoin(source_url, company_website)
            resolved_company_website = urlparse(company_website)
            if (
                resolved_company_website.scheme not in {"http", "https"}
                or not resolved_company_website.netloc
            ):
                company_website = None
        else:
            company_website = None

    return {
        "title": title.strip() if isinstance(title, str) else "",
        "company": company.strip() if isinstance(company, str) else "",
        "location": optional_text(raw_job.get("location")),
        "salary": optional_text(raw_job.get("salary")),
        "description": optional_text(raw_job.get("description")),
        "apply_url": apply_url,
        "company_website": company_website,
        "detail_url": detail_url,
    }


class JobRecommendation(TypedDict):
    """The job data needed by the agent and Telegram job cards."""

    job_id: int
    title: str
    company: str
    location: str | None
    salary: str | None
    apply_url: str | None
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
