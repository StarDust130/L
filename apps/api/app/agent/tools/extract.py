import logging
from urllib.parse import urljoin

from google.genai import types
from google.genai.errors import APIError
from pydantic import BaseModel, Field

from app.agent.tools.jobs import DiscoveredJob
from app.agent.tools.web import fetch_page
from app.core.config import get_settings
from app.llm.client import gemini_client

logger = logging.getLogger(__name__)

settings = get_settings()


class ExtractedJob(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    salary: str | None = None
    description: str | None = None
    detail_url: str | None = None
    apply_url: str | None = None
    company_website: str | None = None


class ExtractedJobsResponse(BaseModel):
    jobs: list[ExtractedJob] = Field(default_factory=list)


async def extract_jobs_from_page(
    page_text: str,
    source_url: str,
) -> list[DiscoveredJob]:
    """
    Extract real job listings from a source page using Gemini.
    """

    if not page_text.strip():
        return []

    prompt = f"""
You are L's job extraction engine.

Extract the real job listings from this webpage.

SOURCE URL:
{source_url}

PAGE CONTENT:
{page_text[:50000]}

RULES:

1. Extract only actual job openings.
2. Do not extract articles, categories, ads, navigation, or company
   descriptions as jobs.
3. Never invent information.
4. Only use information explicitly present on the page.
5. Missing information must be null.
6. Extract these fields whenever available:
   - title
   - company
   - location
   - salary
   - description
   - detail_url
   - apply_url
   - company_website

7. For job-board listing pages:
   - detail_url should point to the individual job page.
   - apply_url should be the direct application URL if visible.
8. Do not guess apply_url.
9. Preserve URLs exactly when they are available.
10. Extract all clearly identifiable jobs on the page.

Return JSON only.
"""

    try:
        response = await gemini_client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedJobsResponse,
            ),
        )

    except APIError as error:
        logger.error(
            "❌ Gemini job extraction failed | source=%s | error=%s",
            source_url,
            error,
        )
        return []

    text = response.text or ""

    if not text:
        logger.warning(
            "⚠️ Gemini returned empty extraction | source=%s",
            source_url,
        )
        return []

    try:
        parsed = ExtractedJobsResponse.model_validate_json(text)
    except Exception:
        logger.exception(
            "❌ Invalid Gemini extraction JSON | source=%s",
            source_url,
        )
        return []

    jobs: list[DiscoveredJob] = []

    for item in parsed.jobs:
        job: DiscoveredJob = {
            "title": item.title or "",
            "company": item.company or "",
            "location": item.location or "",
            "salary": item.salary or "",
            "description": item.description or "",
            "detail_url": item.detail_url or "",
            "apply_url": item.apply_url or "",
            "company_website": item.company_website or "",
        }

        jobs.append(job)

    logger.info(
        "📋 Gemini jobs extracted | source=%s | count=%s",
        source_url,
        len(jobs),
    )

    return jobs


class JobDetail(BaseModel):
    title: str | None = None
    company: str | None = None
    location: str | None = None
    salary: str | None = None
    description: str | None = None
    detail_url: str | None = None
    apply_url: str | None = None
    company_website: str | None = None


async def enrich_job_detail(
    job: DiscoveredJob,
    source_url: str,
) -> DiscoveredJob:
    """
    Fetch the individual job page and fill missing job details.
    """

    detail_url = (job.get("detail_url") or "").strip()

    if not detail_url:
        return job

    detail_url = urljoin(
        source_url,
        detail_url,
    )

    page_text = await fetch_page(detail_url)

    if page_text.startswith("PAGE_FETCH_FAILED:"):
        return job

    prompt = f"""
You are L's job detail extractor.

Read this individual job page and extract the job information.

JOB PAGE:
{page_text[:30000]}

RULES:
- Use only information explicitly present on the page.
- Never invent anything.
- Keep missing fields null.
- Extract the direct application URL if the page contains one.
- Prefer the actual Apply button/link over generic company URLs.
- Keep the exact URL.
- Return only structured JSON.

IMPORTANT:
If the page is an actual job posting, extract:
title
company
location
salary
description
detail_url
apply_url
company_website
"""

    try:
        response = await gemini_client.aio.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobDetail,
            ),
        )

    except APIError as error:
        logger.warning(
            "⚠️ job_detail_gemini_failed | url=%s | error=%s",
            detail_url,
            error,
        )
        return job

    text = response.text or ""

    if not text:
        return job

    try:
        data = JobDetail.model_validate_json(text)
    except Exception:
        logger.warning(
            "⚠️ job_detail_invalid_json | url=%s",
            detail_url,
        )
        return job

    enriched = dict(job)

    fields = (
        "title",
        "company",
        "location",
        "salary",
        "description",
        "detail_url",
        "apply_url",
        "company_website",
    )

    for field in fields:
        value = getattr(data, field)

        if not value:
            continue

        value = value.strip()

        if value:
            enriched[field] = value

    # Always keep the resolved detail URL.
    enriched["detail_url"] = detail_url

    logger.info(
        "✨ job_detail_enriched | title=%s | apply_url=%s",
        enriched.get("title"),
        bool(enriched.get("apply_url")),
    )

    return enriched
