from dataclasses import dataclass

from app.job.job_model import Job
from app.job.matching.ai_matching_service import calculate_compatibility_score
from app.job.recommendation_model import Recommendation
from app.profile.profile_model import CandidateProfileRecord
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class RuleFilterResult:
    """Result of the cheap rule-based job filter."""

    passed: bool
    reasons: list[str]
    matched_skills: list[str]


def rule_based_filter(
    profile: CandidateProfileRecord,
    job: Job,
) -> RuleFilterResult:
    """Apply cheap rules before sending a job to the AI."""

    # 👤 Get candidate preferences
    candidate = profile.profile

    preferred_locations = candidate.get("preferred_locations", [])
    preferred_roles = candidate.get("preferred_roles", [])
    skills = candidate.get("skills", [])

    reasons: list[str] = []
    matched_skills: list[str] = []

    # 🔎 Prepare job text for searching
    job_title = job.title.lower()
    job_location = (job.location or "").lower()

    job_text = " ".join(
        [
            job.title,
            job.description or "",
        ]
    ).lower()

    # 📍 Check location preference
    if preferred_locations:
        location_match = any(
            location.lower() in job_location for location in preferred_locations
        )

        # 🏠 Remote jobs are also allowed
        remote_match = "remote" in job_location

        # ❌ Reject if location does not match
        if not location_match and not remote_match:
            return RuleFilterResult(
                passed=False,
                reasons=["location_mismatch"],
                matched_skills=[],
            )

        # ✅ Location is okay
        reasons.append("location_match")

    # 💼 Check role preference
    if preferred_roles:
        role_match = any(role.lower() in job_title for role in preferred_roles)

        # ❌ Reject if role does not match
        if not role_match:
            return RuleFilterResult(
                passed=False,
                reasons=["role_mismatch"],
                matched_skills=[],
            )

        # ✅ Role is okay
        reasons.append("role_match")

    # 🧠 Find skills mentioned in the job
    for skill in skills:
        if skill.lower() in job_text:
            matched_skills.append(skill)

    # ✅ Skills are a positive signal, not a rejection rule
    if matched_skills:
        reasons.append("skill_match")

    # 📦 Make sure the job has enough data
    if job.title and (job.description or job.apply_url):
        reasons.append("usable_job_data")
    else:
        # ❌ Not enough information to send to AI
        return RuleFilterResult(
            passed=False,
            reasons=["insufficient_job_data"],
            matched_skills=matched_skills,
        )

    # 🚀 Job passed the basic filters
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
    """Filter jobs, score them with AI, and save recommendations."""

    # 💼 Get jobs from PostgreSQL.
    result = await db.execute(select(Job))

    jobs = result.scalars().all()

    saved_count = 0

    for job in jobs:
        # 🧹 Cheap filter first.
        filter_result = rule_based_filter(profile, job)

        if not filter_result.passed:
            continue

        # 🚫 Don't score an already processed job.
        existing = await db.execute(
            select(Recommendation).where(
                Recommendation.clerk_user_id == profile.clerk_user_id,
                Recommendation.job_id == job.id,
            )
        )

        if existing.scalar_one_or_none():
            continue

        # 🤖 Ask AI for compatibility score.
        ai_result = await calculate_compatibility_score(
            profile.profile,
            job,
        )

        # 💾 Save the recommendation.
        recommendation = Recommendation(
            clerk_user_id=profile.clerk_user_id,
            job_id=job.id,
            match_score=ai_result.score,
        )

        db.add(recommendation)
        saved_count += 1

    # 💾 Save all recommendations together.
    await db.commit()

    return saved_count
