import json
import logging

from groq.types.chat import ChatCompletionMessageParam

from app.agent.tools.jobs import JobRecommendation
from app.core.config import get_settings
from app.llm.client import client

logger = logging.getLogger(__name__)

settings = get_settings()


async def extract_jobs_from_page(
    page_text: str,
) -> list[JobRecommendation]:
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
            "apply_url": "string"
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

    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        temperature=0,
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    if not content:
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        logger.warning("⚠️ Job extractor returned invalid JSON")
        return []

    jobs = data.get("jobs", [])

    if not isinstance(jobs, list):
        return []

    return jobs
