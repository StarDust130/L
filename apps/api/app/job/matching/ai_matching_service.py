import json
import logging

from app.core.config import get_settings
from app.job.job_model import Job
from app.job.matching.matching_schema import AICompatibilityResult
from app.llm.client import client

logger = logging.getLogger(__name__)

settings = get_settings()


async def calculate_compatibility_score(
    profile: dict,
    job: Job,
) -> AICompatibilityResult:
    """Calculate how well a job matches a candidate."""

    # 🧠 Give the AI only the data it needs.
    prompt = f"""
You are a job compatibility scorer.

Compare the candidate with the job.

Return ONLY JSON:
{{
    "score": 0
}}

Score from 0 to 100.

Consider:
- Skills
- Experience
- Role relevance
- Location
- Overall fit

Candidate:
{json.dumps(profile, ensure_ascii=False)}

Job:
Title: {job.title}
Location: {job.location or "Unknown"}
Description: {job.description or "No description"}
"""

    logger.info(
        "🤖 ai_matching_started job_id=%s",
        job.id,
    )

    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned empty response")

    # 🛡️ Validate the AI response.
    result = AICompatibilityResult.model_validate_json(content)

    logger.info(
        "🤖 ai_matching_completed job_id=%s score=%s",
        job.id,
        result.score,
    )

    return result
