"""Seed fake job recommendations for a Telegram-linked development user."""

import argparse
import asyncio
import sys
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.company.company_model import Company
from app.db.db import SessionLocal
from app.job.job_model import Job
from app.job.recommendation_model import Recommendation
from app.telegram.telegram_account_model import TelegramAccount


@dataclass(frozen=True)
class SeedJob:
    slug: str
    title: str
    company: str
    location: str
    salary: str
    match_score: float


SEED_JOBS = (
    SeedJob(
        slug="ai-engineer",
        title="AI Engineer",
        company="Northstar AI Labs",
        location="Bengaluru, India (Hybrid)",
        salary="₹28–36 LPA",
        match_score=92,
    ),
    SeedJob(
        slug="backend-engineer",
        title="Backend Engineer",
        company="Vertex Cloud Systems",
        location="Remote, India",
        salary="₹22–30 LPA",
        match_score=87,
    ),
    SeedJob(
        slug="ml-engineer",
        title="ML Engineer",
        company="Signal Forge",
        location="Mumbai, India (Hybrid)",
        salary="₹24–32 LPA",
        match_score=81,
    ),
)

SEED_SOURCE = "development_seed"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed fake recommendations for a Telegram-linked development user.",
    )
    parser.add_argument(
        "--user-id",
        help="Clerk user ID to seed. Defaults to the only Telegram-linked user.",
    )
    return parser.parse_args()


async def find_user_id(user_id: str | None) -> str:
    if user_id:
        return user_id

    async with SessionLocal() as db:
        accounts = (
            (
                await db.execute(
                    select(TelegramAccount)
                    .where(TelegramAccount.telegram_chat_id.is_not(None))
                    .order_by(TelegramAccount.created_at.asc())
                    .limit(2)
                )
            )
            .scalars()
            .all()
        )

    if not accounts:
        raise RuntimeError(
            "No Telegram-linked user found. Pass --user-id to choose one."
        )

    if len(accounts) > 1:
        raise RuntimeError(
            "More than one Telegram-linked user found. Pass --user-id to choose one.",
        )

    return accounts[0].clerk_user_id


async def get_or_create_company(
    db: AsyncSession,
    seed_job: SeedJob,
) -> Company:
    company = (
        (
            await db.execute(
                select(Company)
                .where(
                    Company.source == SEED_SOURCE,
                    Company.external_id == seed_job.slug,
                )
                .limit(1)
            )
        )
        .scalars()
        .first()
    )

    if company is None:
        company = Company(
            name=seed_job.company,
            website=f"https://example.com/companies/{seed_job.slug}",
            source=SEED_SOURCE,
            external_id=seed_job.slug,
        )
        db.add(company)
        await db.flush()
    else:
        company.name = seed_job.company

    return company


async def get_or_create_job(
    db: AsyncSession,
    company: Company,
    seed_job: SeedJob,
) -> Job:
    job = (
        (
            await db.execute(
                select(Job)
                .where(
                    Job.source == SEED_SOURCE,
                    Job.external_id == seed_job.slug,
                )
                .limit(1)
            )
        )
        .scalars()
        .first()
    )

    if job is None:
        job = Job(
            external_id=seed_job.slug,
            fingerprint=f"development-seed:{seed_job.slug}",
            title=seed_job.title,
            company_id=company.id,
            location=seed_job.location,
            description="Development-only recommendation seed job.",
            salary=seed_job.salary,
            apply_url=f"https://example.com/apply/{seed_job.slug}",
            source=SEED_SOURCE,
        )
        db.add(job)
        await db.flush()
    else:
        job.title = seed_job.title
        job.company_id = company.id
        job.location = seed_job.location
        job.salary = seed_job.salary
        job.apply_url = f"https://example.com/apply/{seed_job.slug}"

    return job


async def seed_recommendations(user_id: str) -> None:
    async with SessionLocal() as db:
        for seed_job in SEED_JOBS:
            company = await get_or_create_company(db, seed_job)
            job = await get_or_create_job(db, company, seed_job)
            recommendation = (
                await db.execute(
                    select(Recommendation).where(
                        Recommendation.clerk_user_id == user_id,
                        Recommendation.job_id == job.id,
                    )
                )
            ).scalar_one_or_none()

            if recommendation is None:
                recommendation = Recommendation(
                    clerk_user_id=user_id,
                    job_id=job.id,
                    match_score=seed_job.match_score,
                )
                db.add(recommendation)
            else:
                recommendation.match_score = seed_job.match_score

        await db.commit()

    print(f"Seeded {len(SEED_JOBS)} recommendations for Telegram-linked user.")


def configure_windows_event_loop() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main() -> None:
    args = parse_args()
    user_id = await find_user_id(args.user_id)
    await seed_recommendations(user_id)


if __name__ == "__main__":
    configure_windows_event_loop()
    asyncio.run(main())
