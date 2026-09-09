"""Optional, bounded semantic fallback for ambiguous job pages.

The normal path must not depend on an LLM. This adapter is intentionally small so
it can be replaced without touching the rest of Worker 2.
"""

import json
import logging
from dataclasses import dataclass

from groq import AsyncGroq

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LLMJobPatch:
    company_name: str | None
    location_text: str | None
    remote_scope: str
    category: str | None
    confidence: float


class SemanticJobJudge:
    def __init__(self) -> None:
        settings = get_settings()
        self.enabled = bool(settings.groq_api_key and settings.groq_api_key != "test")
        self.client = AsyncGroq(api_key=settings.groq_api_key) if self.enabled else None
        self.model = settings.groq_model

    async def judge(self, *, title: str, text: str) -> LLMJobPatch | None:
        if not self.enabled or self.client is None:
            return None

        prompt = f"""You are a strict job-data verifier. Return JSON only.
Decide only from the supplied page text. Never guess.

Fields:
company_name: string|null
location_text: string|null
remote_scope: one of none, india, worldwide, us, other, unknown
category: one of tech, nontech, null
confidence: number 0..1

A remote job is worldwide only when the page explicitly supports worldwide/global/anywhere eligibility.
A job is India-eligible only when India or an India location is explicit.

TITLE:
{title[:500]}

PAGE TEXT:
{text[:12000]}
"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "Extract and verify job facts. Never invent missing facts."},
                    {"role": "user", "content": prompt},
                ],
            )
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            confidence = float(data.get("confidence", 0.0))
            return LLMJobPatch(
                company_name=data.get("company_name"),
                location_text=data.get("location_text"),
                remote_scope=str(data.get("remote_scope") or "unknown"),
                category=data.get("category"),
                confidence=max(0.0, min(1.0, confidence)),
            )
        except Exception as exc:
            logger.warning("Semantic job judge failed: %s", exc)
            return None
