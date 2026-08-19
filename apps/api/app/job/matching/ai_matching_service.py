import json
import logging

from app.core.config import get_settings
from app.job.job_model import Job
from app.job.matching.matching_schema import AICompatibilityResult
from app.llm.client import groq_client

logger = logging.getLogger(__name__)

settings = get_settings()


async def calculate_compatibility_score(
    profile: dict,
    job: Job,
) -> AICompatibilityResult:
    """🤖 Score how relevant one job is to one candidate."""

    prompt = f"""
You are a strict job compatibility scorer.

Score how well this job matches this candidate.

Return ONLY valid JSON:
{{
    "score": 0
}}

Score from 0 to 100.

Use these signals:

1. Role relevance
2. Required skills
3. Candidate experience
4. Location / remote preference
5. Overall career fit

Important:
- Do NOT give a high score just because one skill matches.
- If the job is clearly unrelated to the candidate's target roles,
  give a low score.
- If the job is clearly a sales, marketing, HR, finance, or unrelated
  role for a software/AI candidate, score it very low.
- Missing job information should reduce confidence.
- Be strict. A recommendation means the candidate should realistically
  consider applying.

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

    response = await groq_client.chat.completions.create(
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
        raise ValueError("AI returned an empty compatibility score")

    result = AICompatibilityResult.model_validate_json(content)

    logger.info(
        "🤖 ai_matching_completed job_id=%s score=%s",
        job.id,
        result.score,
    )

    return result
