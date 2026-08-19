import re
from dataclasses import dataclass
from urllib.parse import urlparse

from app.agent.tools.jobs import DiscoveredJob


@dataclass(frozen=True)
class JobQualityResult:
    passed: bool
    reason: str


_NON_TARGET_ROLE_TERMS = (
    "recruiter",
    "recruiting",
    "human resources",
    "hr manager",
    "sales",
    "account executive",
    "account manager",
    "customer success",
    "customer service",
    "operations",
    "finance",
    "accounting",
    "payroll",
    "legal",
    "marketing",
    "public relations",
    "administrative",
    "executive assistant",
    "business development",
    "commercial lead",
)


def _contains_term(text: str, term: str) -> bool:
    return (
        re.search(
            rf"\b{re.escape(term)}\b",
            text,
            flags=re.IGNORECASE,
        )
        is not None
    )


def filter_job_quality(
    job: DiscoveredJob,
) -> JobQualityResult:
    """
    Cheap hard filter.

    Only reject obvious junk.
    Gemini handles the actual user/job matching.
    """

    if not isinstance(job, dict):
        return JobQualityResult(
            passed=False,
            reason="invalid_job_shape",
        )

    title = str(job.get("title") or "").strip().lower()

    if not title:
        return JobQualityResult(
            passed=False,
            reason="missing_title",
        )

    for term in _NON_TARGET_ROLE_TERMS:
        if _contains_term(title, term):
            return JobQualityResult(
                passed=False,
                reason=f"non_target_role:{term}",
            )

    return JobQualityResult(
        passed=True,
        reason="passed_hard_filter",
    )


def validate_job(job: DiscoveredJob) -> str | None:
    """Validate required job fields."""

    if not isinstance(job, dict):
        return "invalid_job_shape"

    title = str(job.get("title") or "").strip()
    company = str(job.get("company") or "").strip()
    apply_url = str(job.get("apply_url") or "").strip()

    if not title:
        return "missing_title"

    if not company:
        return "missing_company"

    if not apply_url:
        return None

    parsed = urlparse(apply_url)

    if parsed.scheme not in {"http", "https"}:
        return "invalid_url_scheme"

    if not parsed.netloc:
        return "missing_url_host"

    return None
