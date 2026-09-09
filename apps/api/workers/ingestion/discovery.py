from dataclasses import dataclass
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from .sources import SourceProfile


@dataclass(frozen=True)
class CandidateURL:
    url: str
    title: str
    source_url: str


def _same_domain(url: str, domain: str) -> bool:
    host = (urlsplit(url).hostname or "").lower().removeprefix("www.")
    domain = domain.lower().removeprefix("www.")
    return host == domain or host.endswith("." + domain)


def discover_job_links(html: str, page_url: str, profile: SourceProfile) -> list[CandidateURL]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[CandidateURL] = []
    seen: set[str] = set()

    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "").strip()
        if not href:
            continue
        url = urljoin(page_url, href)
        parts = urlsplit(url)
        if parts.scheme not in {"http", "https"} or not _same_domain(url, profile.domain):
            continue
        normalized = url.split("#", 1)[0].rstrip("/")
        if normalized in seen:
            continue

        lower = normalized.lower()
        if any(term.lower() in lower for term in profile.exclude_url_terms):
            continue
        if not any(term.lower() in lower for term in profile.include_url_terms):
            # A job-looking anchor can still be useful on JS/modern sites.
            anchor_text = anchor.get_text(" ", strip=True).lower()
            if not any(hint in lower or hint.strip("/") in anchor_text for hint in profile.job_link_hints):
                continue

        title = anchor.get_text(" ", strip=True)
        if len(title) > 300:
            title = title[:300]
        seen.add(normalized)
        candidates.append(CandidateURL(url=normalized, title=title, source_url=page_url))
        if len(candidates) >= profile.max_job_urls_per_page:
            break

    return candidates
