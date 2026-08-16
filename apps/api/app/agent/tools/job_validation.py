from urllib.parse import urlparse

from app.agent.tools.jobs import DiscoveredJob


def validate_job(job: DiscoveredJob) -> str | None:
    """🧹 Validate a discovered job.

    Returns:
        None if valid.
        A reason string if invalid.
    """

    if not isinstance(job, dict):
        return "invalid_job_shape"

    title = job.get("title")
    company = job.get("company")
    apply_url = job.get("apply_url")

    if not isinstance(title, str):
        title = ""
    if not isinstance(company, str):
        company = ""
    if not isinstance(apply_url, str):
        apply_url = ""

    title = title.strip()
    company = company.strip()
    apply_url = apply_url.strip()

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
