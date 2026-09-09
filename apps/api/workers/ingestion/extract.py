import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlsplit

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class ExtractedJob:
    title: str
    company_name: str | None
    description: str | None
    canonical_url: str
    apply_url: str | None
    location_text: str | None
    locations: list[str]
    remote: bool
    remote_scope: str
    eligible_countries: list[str]
    employment_type: str | None
    salary_text: str | None
    posted_at: datetime | None
    external_id: str | None
    extraction_confidence: float
    method: str
    evidence: dict


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text or None


def _jsonld_objects(soup: BeautifulSoup) -> list[dict]:
    objects: list[dict] = []
    for node in soup.select('script[type="application/ld+json"]'):
        raw = node.string or node.get_text()
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            continue
        values = data if isinstance(data, list) else [data]
        for item in values:
            if isinstance(item, dict):
                if "@graph" in item and isinstance(item["@graph"], list):
                    objects.extend(x for x in item["@graph"] if isinstance(x, dict))
                else:
                    objects.append(item)
    return objects


def _jobposting(objects: list[dict]) -> dict | None:
    for item in objects:
        types = item.get("@type")
        if types == "JobPosting" or (isinstance(types, list) and "JobPosting" in types):
            return item
    return None


def _locations(job: dict) -> list[str]:
    out: list[str] = []
    location = job.get("jobLocation")
    values = location if isinstance(location, list) else [location]
    for item in values:
        if isinstance(item, dict):
            address = item.get("address", item)
            if isinstance(address, dict):
                bits = [address.get("addressLocality"), address.get("addressRegion"), address.get("addressCountry")]
                text = ", ".join(str(x) for x in bits if x)
                if text:
                    out.append(text)
    return list(dict.fromkeys(out))


def _country_names(job: dict) -> list[str]:
    out: list[str] = []
    value = job.get("applicantLocationRequirements")
    values = value if isinstance(value, list) else [value]
    for item in values:
        if isinstance(item, dict):
            country = item.get("name") or item.get("value")
            if country:
                out.append(str(country))
        elif item:
            out.append(str(item))
    return list(dict.fromkeys(out))


def _parse_date(value: object) -> datetime | None:
    if not value:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _infer_remote(text: str) -> tuple[bool, str]:
    lower = text.lower()
    if not any(x in lower for x in ("remote", "work from home", "distributed")):
        return False, "none"
    if any(x in lower for x in ("worldwide", "anywhere in the world", "global", "work from anywhere")):
        return True, "worldwide"
    if any(x in lower for x in ("remote - india", "remote india", "india remote", "remote within india")):
        return True, "india"
    if any(x in lower for x in ("remote - us", "remote us", "united states only", "us only")):
        return True, "us"
    return True, "unknown"


def extract_job(html: str, page_url: str, anchor_title: str | None = None) -> ExtractedJob | None:
    soup = BeautifulSoup(html, "html.parser")
    objects = _jsonld_objects(soup)
    job = _jobposting(objects)

    if job:
        title = _clean(job.get("title")) or anchor_title
        if not title:
            return None
        company = job.get("hiringOrganization")
        company_name = _clean(company.get("name")) if isinstance(company, dict) else _clean(company)
        locations = _locations(job)
        countries = _country_names(job)
        description = _clean(BeautifulSoup(str(job.get("description", "")), "html.parser").get_text(" "))
        remote, scope = _infer_remote(" ".join([description or "", " ".join(locations), " ".join(countries)]))
        if job.get("jobLocationType") == "TELECOMMUTE":
            remote = True
            if scope == "none":
                scope = "unknown"
        apply_url = None
        direct_apply = job.get("directApply")
        if isinstance(direct_apply, str):
            apply_url = direct_apply
        canonical = _clean(job.get("url")) or page_url
        external_id = _clean(job.get("identifier", {}).get("value")) if isinstance(job.get("identifier"), dict) else None
        return ExtractedJob(
            title=title,
            company_name=company_name,
            description=description,
            canonical_url=canonical,
            apply_url=apply_url or page_url,
            location_text=", ".join(locations) or None,
            locations=locations,
            remote=remote,
            remote_scope=scope,
            eligible_countries=countries,
            employment_type=_clean(job.get("employmentType")),
            salary_text=_clean(job.get("baseSalary")),
            posted_at=_parse_date(job.get("datePosted")),
            external_id=external_id,
            extraction_confidence=0.95,
            method="jsonld",
            evidence={"jsonld": True, "jobposting": True, "page_url": page_url},
        )

    # Conservative fallback: title + visible text. We deliberately do not invent company/location.
    title = anchor_title or _clean(soup.title.get_text(" ")) if soup.title else anchor_title
    if not title:
        return None
    text = _clean(soup.get_text(" ", strip=True)) or ""
    lower = text.lower()
    job_signals = sum(
        1 for marker in ("responsibilities", "requirements", "qualifications", "apply", "experience", "job description")
        if marker in lower
    )
    if job_signals < 2:
        return None
    remote, scope = _infer_remote(text[:20_000])
    return ExtractedJob(
        title=title[:500],
        company_name=None,
        description=text[:50_000],
        canonical_url=page_url,
        apply_url=page_url,
        location_text=None,
        locations=[],
        remote=remote,
        remote_scope=scope,
        eligible_countries=[],
        employment_type=None,
        salary_text=None,
        posted_at=None,
        external_id=None,
        extraction_confidence=0.55,
        method="visible_text",
        evidence={"jsonld": False, "job_signals": job_signals, "page_url": page_url},
    )


def dedupe_key(job: ExtractedJob) -> str:
    if job.external_id:
        raw = f"{job.company_name or ''}|{job.external_id}|{job.canonical_url.split('?')[0]}"
    else:
        raw = "|".join(
            [
                (job.company_name or "").lower().strip(),
                job.title.lower().strip(),
                (job.location_text or "").lower().strip(),
            ]
        )
    return hashlib.sha256(raw.encode()).hexdigest()
