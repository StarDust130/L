from dataclasses import dataclass

from .extract import ExtractedJob

INDIA_TERMS = ("india", "indian", "bangalore", "bengaluru", "mumbai", "delhi", "gurugram", "gurgaon", "hyderabad", "pune", "chennai", "noida", "kolkata", "ahmedabad")
US_TERMS = ("united states", "usa", "u.s.", "us only", "california", "new york", "texas")
WORLD_TERMS = ("worldwide", "global", "anywhere in the world", "work from anywhere")

TECH_TERMS = ("software", "frontend", "front end", "backend", "back end", "full stack", "full-stack", "developer", "engineer", "ai", "machine learning", "data", "devops", "cloud", "cybersecurity", "security", "product engineer")
NONTECH_TERMS = ("hr", "human resources", "recruiter", "recruiting", "marketing", "sales", "founder", "founder's office", "operations", "product", "program manager", "customer success")


@dataclass(frozen=True)
class QualityDecision:
    accepted: bool
    score: float
    category: str | None
    reason: str
    remote_scope: str
    eligibility_confidence: float


def evaluate_job(job: ExtractedJob) -> QualityDecision:
    title = job.title.lower()
    text = f"{job.title} {job.company_name or ''} {job.location_text or ''} {job.description or ''}".lower()

    if len(job.title.strip()) < 3:
        return QualityDecision(False, 0.0, None, "missing_or_invalid_title", job.remote_scope, 0.0)

    category = None
    if any(term in title or term in text for term in TECH_TERMS):
        category = "tech"
    elif any(term in title or term in text for term in NONTECH_TERMS):
        category = "nontech"

    if category is None:
        return QualityDecision(False, 0.15, None, "outside_v1_job_categories", job.remote_scope, 0.2)

    location_text = f"{job.location_text or ''} {' '.join(job.eligible_countries)} {job.description or ''}".lower()
    india = any(term in location_text for term in INDIA_TERMS)
    worldwide = job.remote_scope == "worldwide" or any(term in location_text for term in WORLD_TERMS)
    us_only = any(term in location_text for term in US_TERMS) and not india and not worldwide

    if us_only:
        return QualityDecision(False, 0.25, category, "not_india_or_worldwide", job.remote_scope, 0.95)

    if job.remote and job.remote_scope == "unknown" and not india:
        return QualityDecision(False, 0.45, category, "remote_eligibility_unknown", job.remote_scope, 0.4)

    eligible = india or worldwide or (job.remote and job.remote_scope == "india")
    if not eligible:
        return QualityDecision(False, 0.35, category, "location_not_supported_for_v1", job.remote_scope, 0.9)

    score = 0.5
    if job.company_name:
        score += 0.15
    if job.description and len(job.description) >= 500:
        score += 0.15
    if job.apply_url:
        score += 0.1
    if job.posted_at:
        score += 0.1
    return QualityDecision(True, min(score, 1.0), category, "accepted", job.remote_scope, 0.9 if india or worldwide else 0.7)
