from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.job.job_model import Job
from app.job.matching.ai_matching_service import calculate_compatibility_score
from app.job.recommendation_model import Recommendation
from app.profile.profile_model import CandidateProfileRecord


@dataclass
class RuleFilterResult:
    """🧹 Cheap pre-filter result."""

    passed: bool
    reasons: list[str]
    matched_skills: list[str]


def rule_based_filter(
    profile: CandidateProfileRecord,
    job: Job,
) -> RuleFilterResult:
    """🧹 Remove only obviously unusable jobs before AI scoring."""

    candidate = profile.profile

    skills = candidate.get("skills", [])

    reasons: list[str] = []
    matched_skills: list[str] = []

    # ❌ No title = unusable job.
    if not job.title:
        return RuleFilterResult(
            passed=False,
            reasons=["missing_title"],
            matched_skills=[],
        )

    # ❌ No way to apply = unusable job.
    if not job.apply_url:
        return RuleFilterResult(
            passed=False,
            reasons=["missing_apply_url"],
            matched_skills=[],
        )

    # 🧠 Search title + description for candidate skills.
    job_text = " ".join(
        [
            job.title,
            job.description or "",
        ]
    ).lower()

    for skill in skills:
        if skill.lower() in job_text:
            matched_skills.append(skill)

    if matched_skills:
        reasons.append("skill_match")

    reasons.append("usable_job_data")

    # ✅ Don't reject because of role/location.
    # AI will decide whether the job is actually a good match.
    return RuleFilterResult(
        passed=True,
        reasons=reasons,
        matched_skills=matched_skills,
    )


"""
🚀 Better alternatives to add later:-

🔤 Normalize text
Handle NYC = New York, JS = JavaScript, etc.
🧩 Synonym matching
Backend Engineer ≈ Backend Developer
📊 Score instead of hard filter
Example: location 40% + role 40% + skills 20%.
🔎 Keyword/phrase matching
Better than simple in matching.
🧠 Embeddings / semantic search
Understand that "Python backend developer" and "Django engineer" can be related.
🤖 AI as final judge
Keep this cheap filter first, then let AI make the smarter decision.
⭐ Best future architecture

Cheap rules → scoring → semantic/embedding match → AI final decision
"""


async def match_jobs_for_user(
    db: AsyncSession,
    profile: CandidateProfileRecord,
) -> int:
    """🎯 Find and save strong job matches for one user."""

    # 💼 Get all discovered jobs.
    # These are the global job pool, NOT recommendations.
    result = await db.execute(select(Job))

    jobs = result.scalars().all()

    saved_count = 0

    for job in jobs:
        # 🧹 Cheap deterministic filter.
        # Only removes obviously unusable jobs.
        filter_result = rule_based_filter(
            profile,
            job,
        )

        if not filter_result.passed:
            continue

        # 🚫 Don't score the same user/job pair twice.
        result = await db.execute(
            select(Recommendation).where(
                Recommendation.clerk_user_id == profile.clerk_user_id,
                Recommendation.job_id == job.id,
            )
        )

        if result.scalar_one_or_none():
            continue

        # 🤖 AI decides whether this job is actually relevant.
        ai_result = await calculate_compatibility_score(
            profile.profile,
            job,
        )

        # ❌ Weak match → keep the job in `jobs`,
        # but don't create a recommendation.
        if ai_result.score < 10: # TODO: -> MAKE IT 60% in production
            continue

        # 💾 Strong match → create user-specific recommendation.
        recommendation = Recommendation(
            clerk_user_id=profile.clerk_user_id,
            job_id=job.id,
            match_score=ai_result.score,
        )

        db.add(recommendation)

        saved_count += 1

    # 💾 Save all strong recommendations together.
    await db.commit()

    return saved_count