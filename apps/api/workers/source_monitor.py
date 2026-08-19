import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any

from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.memory.memory_model import UserMemory
from app.agent.tools.extract import extract_jobs_from_page
from app.agent.tools.job_persistence import make_job_fingerprint, save_discovered_job
from app.agent.tools.job_validation import (
    filter_job_quality,
    validate_job,
)
from app.agent.tools.jobs import DiscoveredJob, normalize_discovered_job
from app.agent.tools.web import fetch_page
from app.core.config import get_settings
from app.job.job_model import Job
from app.job.recommendation_model import Recommendation
from app.llm.client import gemini_client
from app.profile.profile_model import CandidateProfileRecord
from app.source.source_model import Source
from workers.source_scheduler import should_check_source

logger = logging.getLogger(__name__)

settings = get_settings()


MIN_MATCH_SCORE = 0.60
DETAIL_FETCH_CONCURRENCY = 8
MAX_DETAIL_TEXT = 5_000

# Gemini can handle large batches.
GEMINI_BATCH_SIZE = 50


class EvaluatedJob(BaseModel):
    index: int

    title: str = ""
    company: str = ""
    location: str = ""
    salary: str = ""
    description: str = ""
    detail_url: str = ""
    apply_url: str = ""
    company_website: str = ""

    match_score: float = Field(
        ge=0.0,
        le=1.0,
    )

    match_reason: str = ""


class EvaluatedJobsResponse(BaseModel):
    jobs: list[EvaluatedJob] = Field(default_factory=list)


async def fetch_detail_pages(
    jobs: list[DiscoveredJob],
) -> dict[int, str]:
    """
    Fetch job detail pages with Python only.

    No Gemini call here.
    """

    semaphore = asyncio.Semaphore(DETAIL_FETCH_CONCURRENCY)

    async def fetch_one(
        index: int,
        job: DiscoveredJob,
    ) -> tuple[int, str]:
        detail_url = (job.get("detail_url") or "").strip()

        if not detail_url:
            return index, ""

        async with semaphore:
            page = await fetch_page(detail_url)

        if page.startswith("PAGE_FETCH_FAILED:"):
            logger.warning(
                "⚠️ detail_fetch_failed | index=%s | url=%s",
                index,
                detail_url,
            )
            return index, ""

        return index, page[:MAX_DETAIL_TEXT]

    results = await asyncio.gather(
        *(fetch_one(index, job) for index, job in enumerate(jobs))
    )

    return {index: page for index, page in results if page}


async def evaluate_jobs_with_gemini(
    jobs: list[DiscoveredJob],
    detail_pages: dict[int, str],
    profile: dict[str, Any],
    memory: dict[str, Any],
) -> list[EvaluatedJob]:
    """
    ONE Gemini request:

    - complete missing job data
    - inspect detail-page content
    - match against candidate
    - score the job
    """

    if not jobs:
        return []

    payload: list[dict[str, Any]] = []

    for index, job in enumerate(jobs):
        payload.append(
            {
                "index": index,
                "job": {
                    "title": job.get("title", ""),
                    "company": job.get("company", ""),
                    "location": job.get("location", ""),
                    "salary": job.get("salary", ""),
                    "description": (job.get("description") or "")[:2_000],
                    "detail_url": (job.get("detail_url") or ""),
                    "apply_url": (job.get("apply_url") or ""),
                    "company_website": (job.get("company_website") or ""),
                },
                "detail_page": detail_pages.get(
                    index,
                    "",
                ),
            }
        )

    prompt = f"""
You are L's final job evaluation engine.

You receive:
1. Candidate profile
2. Candidate long-term memory
3. Job listings
4. Individual job-page content when available

Your job is to COMPLETE and SCORE every job.

CANDIDATE PROFILE:
{json.dumps(profile, default=str)}

CANDIDATE MEMORY:
{json.dumps(memory, default=str)}

JOBS:
{json.dumps(payload, default=str)}

RULES FOR JOB DATA:

- Use the individual detail page when available.
- Prefer detail-page information over listing-page information.
- Fill missing company, location, description, salary, apply_url,
  company_website, and detail_url when clearly present.
- Never invent information.
- If information is unavailable, leave it empty.
- The direct Apply URL is preferred.
- Do not use a generic homepage as apply_url.
- Preserve real URLs exactly when available.

RULES FOR MATCHING:

- Compare the job with the candidate's actual skills,
  experience, projects, technologies, and career direction.
- Use long-term memory for preferences.
- Do NOT require an exact title match.
- Full-stack experience can match backend/software/AI roles.
- Python/backend/API experience can transfer to AI/ML/software roles.
- Missing one requirement does not automatically make the job bad.
- Respect explicit hard requirements.
- Normal preferences are strong signals, not absolute restrictions.
- Prefer technical engineering opportunities.
- Clearly unrelated roles should receive a very low score.
- Do not invent candidate experience.
- Do not invent job requirements.

SCORING:

0.90 - 1.00 = exceptional
0.80 - 0.89 = excellent
0.70 - 0.79 = strong
0.60 - 0.69 = good
0.50 - 0.59 = possible
0.40 - 0.49 = weak but relevant
0.00 - 0.39 = poor

The score is for ranking opportunities.

Return one result for every input job.

Return ONLY structured JSON.
"""

    try:
        response = await gemini_client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=EvaluatedJobsResponse,
            ),
        )

    except APIError as error:
        logger.error(
            "❌ Gemini evaluation failed | error=%s",
            error,
        )
        return []

    text = response.text or ""

    if not text:
        logger.error("❌ Gemini evaluation returned empty response")
        return []

    try:
        parsed = EvaluatedJobsResponse.model_validate_json(text)
    except Exception:
        logger.exception("❌ Invalid Gemini evaluation JSON")
        return []

    return parsed.jobs


async def _load_user_context(
    db: AsyncSession,
    user_id: str,
) -> tuple[dict, dict]:
    """
    Load candidate profile + long-term memory.
    """

    profile_result = await db.execute(
        select(CandidateProfileRecord).where(
            CandidateProfileRecord.clerk_user_id == user_id,
        )
    )

    profile_record = profile_result.scalar_one_or_none()

    if profile_record is None:
        return {}, {}

    profile = profile_record.profile if isinstance(profile_record.profile, dict) else {}

    memory_result = await db.execute(
        select(UserMemory).where(
            UserMemory.clerk_user_id == user_id,
        )
    )

    memory_record = memory_result.scalar_one_or_none()

    memory = (
        memory_record.memory
        if memory_record and isinstance(memory_record.memory, dict)
        else {}
    )

    return profile, memory


async def _save_recommendation(
    db: AsyncSession,
    user_id: str,
    job_id: int,
    score: float,
) -> tuple[bool, bool]:
    """
    Create or update a recommendation.

    Returns:
        (created, updated)
    """

    result = await db.execute(
        select(Recommendation).where(
            Recommendation.clerk_user_id == user_id,
            Recommendation.job_id == job_id,
        )
    )

    recommendation = result.scalar_one_or_none()

    if recommendation is None:
        db.add(
            Recommendation(
                clerk_user_id=user_id,
                job_id=job_id,
                match_score=score,
            )
        )

        return True, False

    # Update score if Gemini has a newer evaluation.
    if float(recommendation.match_score) != score:
        recommendation.match_score = score

        return False, True

    return False, False


async def monitor_sources(
    db: AsyncSession,
    user_id: str,
) -> dict[str, int]:
    """
    Monitor known sources and build user-specific recommendations.

    Pipeline:

        Source
          ↓
        fetch source page
          ↓
        Gemini: extract jobs
          ↓
        cheap Python filter
          ↓
        fetch detail pages with HTTP
          ↓
        Gemini: enrich + match + score
          ↓
        validate
          ↓
        save/update Job
          ↓
        create/update Recommendation
    """

    logger.info(
        "🔎 source_monitor_started | user=%s",
        user_id,
    )

    profile, memory = await _load_user_context(
        db=db,
        user_id=user_id,
    )

    if not profile:
        logger.warning(
            "⚠️ No candidate profile found | user=%s",
            user_id,
        )

        return {
            "sources_checked": 0,
            "sources_failed": 0,
            "jobs_found": 0,
            "hard_rejected": 0,
            "invalid_jobs": 0,
            "weak_matches": 0,
            "duplicate_jobs": 0,
            "new_jobs_saved": 0,
            "recommendations_created": 0,
            "recommendations_updated": 0,
        }

    # ---------------------------------------------------------
    # Load sources.
    # ---------------------------------------------------------

    result = await db.execute(
        select(Source).order_by(
            Source.quality_score.desc(),
            Source.last_checked.asc(),
        )
    )

    sources = result.scalars().all()

    sources_to_check = [source for source in sources if should_check_source(source)]

    logger.info(
        "📅 sources scheduled | total=%s | checking=%s",
        len(sources),
        len(sources_to_check),
    )

    sources_checked = 0
    sources_failed = 0
    jobs_found = 0
    hard_rejected = 0
    invalid_jobs = 0
    weak_matches = 0
    duplicate_jobs = 0
    new_jobs_saved = 0
    recommendations_created = 0
    recommendations_updated = 0

    # ---------------------------------------------------------
    # Process each source.
    # ---------------------------------------------------------

    for source in sources_to_check:
        logger.info(
            "🔄 source_check_started | source=%s | quality=%.1f",
            source.name,
            source.quality_score,
        )

        try:
            # -------------------------------------------------
            # 1. Fetch source page.
            # -------------------------------------------------

            page_text = await fetch_page(
                source.url,
            )

            if page_text.startswith("PAGE_FETCH_FAILED:"):
                source.failure_count += 1
                sources_failed += 1

                logger.warning(
                    "⚠️ source_fetch_failed | source=%s | failures=%s",
                    source.name,
                    source.failure_count,
                )

                continue

            # -------------------------------------------------
            # 2. Gemini #1:
            #    Extract jobs from the source.
            # -------------------------------------------------

            raw_jobs = await extract_jobs_from_page(
                page_text=page_text,
                source_url=source.url,
            )

            jobs_found += len(raw_jobs)

            logger.info(
                "📋 jobs_extracted | source=%s | count=%s",
                source.name,
                len(raw_jobs),
            )

            # -------------------------------------------------
            # 3. Normalize + cheap Python filter.
            # -------------------------------------------------

            candidate_jobs: list[DiscoveredJob] = []

            for raw_job in raw_jobs:
                try:
                    job = normalize_discovered_job(
                        raw_job,
                        source.url,
                    )

                    if job is None:
                        invalid_jobs += 1
                        continue

                    quality_result = filter_job_quality(
                        job,
                    )

                    if not quality_result.passed:
                        hard_rejected += 1

                        logger.info(
                            "🚫 hard_filter_rejected | "
                            "source=%s | title=%s | reason=%s",
                            source.name,
                            job.get("title"),
                            quality_result.reason,
                        )

                        continue

                    candidate_jobs.append(job)

                except Exception:
                    invalid_jobs += 1

                    logger.exception(
                        "❌ job_normalization_failed | source=%s",
                        source.name,
                    )

            if not candidate_jobs:
                source.last_checked = datetime.now(UTC)
                source.failure_count = 0
                sources_checked += 1

                logger.info(
                    "✅ source_check_completed | source=%s | jobs=0",
                    source.name,
                )

                continue

            # -------------------------------------------------
            # 4. Fetch detail pages with normal HTTP.
            #
            # NO Gemini here.
            #
            # This gives Gemini richer information later.
            # -------------------------------------------------

            detail_pages = await fetch_detail_pages(
                jobs=candidate_jobs,
            )

            logger.info(
                "🌐 detail_pages_fetched | source=%s | count=%s",
                source.name,
                len(detail_pages),
            )

            # -------------------------------------------------
            # 5. Gemini #2:
            #
            # ONE request:
            #   - enrich missing fields
            #   - inspect detail pages
            #   - compare against profile
            #   - use memory
            #   - calculate match score
            # -------------------------------------------------

            for start in range(
                0,
                len(candidate_jobs),
                GEMINI_BATCH_SIZE,
            ):
                batch = candidate_jobs[start : start + GEMINI_BATCH_SIZE]

                # Detail pages are indexed relative to the
                # original candidate list, so remap them.
                batch_detail_pages: dict[int, str] = {}

                for batch_index, job in enumerate(batch):
                    global_index = start + batch_index

                    detail = detail_pages.get(
                        global_index,
                    )

                    if detail:
                        batch_detail_pages[batch_index] = detail

                evaluated_jobs = await evaluate_jobs_with_gemini(
                    jobs=batch,
                    detail_pages=batch_detail_pages,
                    profile=profile,
                    memory=memory,
                )

                logger.info(
                    "🧠 Gemini evaluated | source=%s | count=%s",
                    source.name,
                    len(evaluated_jobs),
                )

                # -------------------------------------------------
                # 6. Save jobs + recommendations.
                # -------------------------------------------------

                for evaluated in evaluated_jobs:
                    score = float(evaluated.match_score)

                    if score < MIN_MATCH_SCORE:
                        weak_matches += 1

                        logger.info(
                            "🚫 weak_user_match | source=%s | title=%s | score=%.2f",
                            source.name,
                            evaluated.title,
                            score,
                        )

                        continue

                    job = normalize_discovered_job(
                        {
                            "title": evaluated.title,
                            "company": evaluated.company,
                            "location": evaluated.location,
                            "salary": evaluated.salary,
                            "description": evaluated.description,
                            "detail_url": evaluated.detail_url,
                            "apply_url": evaluated.apply_url,
                            "company_website": (evaluated.company_website),
                        },
                        source.url,
                    )

                    if job is None:
                        invalid_jobs += 1
                        continue

                    validation_error = validate_job(
                        job,
                    )

                    if validation_error:
                        invalid_jobs += 1

                        logger.warning(
                            "⚠️ invalid_job | source=%s | title=%s | reason=%s",
                            source.name,
                            job.get("title"),
                            validation_error,
                        )

                        continue

                    # -------------------------------------------------
                    # 7. Save or update job.
                    # -------------------------------------------------

                    changed = await save_discovered_job(
                        db=db,
                        job_data=job,
                        source=source.name,
                    )

                    if changed:
                        new_jobs_saved += 1

                        logger.info(
                            "💾 job_saved_or_updated | "
                            "source=%s | title=%s | score=%.2f",
                            source.name,
                            job.get("title"),
                            score,
                        )
                    else:
                        duplicate_jobs += 1

                        logger.info(
                            "♻️ job_unchanged | source=%s | title=%s",
                            source.name,
                            job.get("title"),
                        )

                    # -------------------------------------------------
                    # 8. Find the saved job.
                    # -------------------------------------------------

                    fingerprint = make_job_fingerprint(
                        job,
                    )

                    job_result = await db.execute(
                        select(Job).where(
                            Job.fingerprint == fingerprint,
                        )
                    )

                    saved_job = job_result.scalar_one_or_none()

                    if saved_job is None:
                        logger.warning(
                            "⚠️ saved job could not be reloaded | title=%s",
                            job.get("title"),
                        )

                        continue

                    # -------------------------------------------------
                    # 9. Recommendation uses SAME Gemini score.
                    #
                    # NO SECOND Gemini call.
                    # -------------------------------------------------

                    (
                        recommendation_created,
                        recommendation_updated,
                    ) = await _save_recommendation(
                        db=db,
                        user_id=user_id,
                        job_id=saved_job.id,
                        score=score,
                    )

                    if recommendation_created:
                        recommendations_created += 1

                        logger.info(
                            "⭐ recommendation_created | job_id=%s | score=%.2f",
                            saved_job.id,
                            score,
                        )

                    elif recommendation_updated:
                        recommendations_updated += 1

                        logger.info(
                            "🔄 recommendation_updated | job_id=%s | score=%.2f",
                            saved_job.id,
                            score,
                        )

            # -------------------------------------------------
            # 10. Source completed.
            # -------------------------------------------------

            source.last_checked = datetime.now(UTC)
            source.failure_count = 0
            sources_checked += 1

            logger.info(
                "✅ source_check_completed | source=%s | jobs=%s",
                source.name,
                len(raw_jobs),
            )

        except Exception:
            sources_failed += 1
            source.failure_count += 1

            logger.exception(
                "❌ source_check_failed | source=%s",
                source.name,
            )

    # ---------------------------------------------------------
    # Final commit.
    # ---------------------------------------------------------

    await db.commit()

    result_data = {
        "sources_checked": sources_checked,
        "sources_failed": sources_failed,
        "jobs_found": jobs_found,
        "hard_rejected": hard_rejected,
        "invalid_jobs": invalid_jobs,
        "weak_matches": weak_matches,
        "duplicate_jobs": duplicate_jobs,
        "new_jobs_saved": new_jobs_saved,
        "recommendations_created": recommendations_created,
        "recommendations_updated": recommendations_updated,
    }

    logger.info(
        "✅ source_monitor_finished | %s",
        result_data,
    )

    return result_data
