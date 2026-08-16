import json
import logging

from groq.types.chat import ChatCompletionMessageParam

from app.agent.tools.jobs import DiscoveredJob, normalize_discovered_job
from app.core.config import get_settings
from app.llm.client import client

logger = logging.getLogger(__name__)

settings = get_settings()


async def extract_jobs_from_page(
    page_text: str,
    source_url: str,
) -> list[DiscoveredJob]:
    """🧠 Extract real job listings from cleaned page text."""

    prompt = f"""
Extract actual job listings from this webpage.

Return ONLY valid JSON:

{{
    "jobs": [
        {{
            "title": "string",
            "company": "string",
            "location": "string or null",
            "salary": "string or null",
            "description": "string or null",
            "apply_url": "string or null"
        }}
    ]
}}

Rules:
- Extract only real job openings.
- Do not invent missing information.
- If no jobs are present, return an empty jobs array.
- Ignore navigation, marketing text, blog posts, and unrelated content.
- Keep descriptions concise.

PAGE:
{page_text[:7000]}
"""

    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "user",
            "content": prompt,
        }
    ]

    try:
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=0,
            response_format={"type": "json_object"},
        )
    except Exception:
        logger.exception("job_extraction_failed source=%s", source_url)
        return []

    try:
        content = response.choices[0].message.content
    except Exception:
        logger.exception("job_extraction_failed reason=invalid_response source=%s", source_url)
        return []

    if not content:
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        logger.warning("⚠️ Job extractor returned invalid JSON")
        return []

    jobs = data.get("jobs", []) if isinstance(data, dict) else []

    if not isinstance(jobs, list):
        return []

    return [
        normalized
        for raw_job in jobs
        if (normalized := normalize_discovered_job(raw_job, source_url)) is not None
    ]
