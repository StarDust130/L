import re
from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup, Tag

YC_BASE_URL = "https://www.ycombinator.com"

# 🎯 Start with India + currently hiring companies.
YC_COMPANIES_URL = f"{YC_BASE_URL}/companies/location/india/hiring"


@dataclass
class YCCompany:
    """🏢 Clean company data discovered from YC."""

    name: str
    yc_url: str
    website: str | None
    description: str | None
    location: str | None
    yc_batch: str | None
    employee_count: int | None
    is_active: bool
    is_hiring: bool
    remote_friendly: bool
    jobs_url: str


async def discover_yc_companies() -> list[YCCompany]:
    """🔎 Discover and enrich YC companies."""

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/151.0 Safari/537.36"
        )
    }

    async with httpx.AsyncClient(
        headers=headers,
        timeout=30.0,
        follow_redirects=True,
    ) as client:
        # 1️⃣ Find companies from YC directory.
        company_urls = await _discover_company_urls(client)

        companies: list[YCCompany] = []

        # 2️⃣ Open each company page and enrich it.
        for yc_url in company_urls:
            try:
                company = await _scrape_company(
                    client,
                    yc_url,
                )

                if company:
                    companies.append(company)

            except httpx.HTTPError:
                # ⚠️ One bad company should not kill the whole run.
                continue

    return companies


async def _discover_company_urls(
    client: httpx.AsyncClient,
) -> list[str]:
    """🔎 Get unique YC company URLs from the directory."""

    response = await client.get(YC_COMPANIES_URL)
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    urls: set[str] = set()

    for link in soup.find_all("a", href=True):
        href = str(link["href"])

        # 🏢 Only company profile pages.
        if not href.startswith("/companies/"):
            continue

        # 🚫 Ignore category/listing pages.
        if href.count("/") != 2:
            continue

        urls.add(
            urljoin(
                YC_BASE_URL,
                href,
            )
        )

    return list(urls)


async def _scrape_company(
    client: httpx.AsyncClient,
    yc_url: str,
) -> YCCompany | None:
    """🏢 Scrape one YC company page + jobs page."""

    response = await client.get(yc_url)
    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    # 🏢 Company name.
    name = _extract_name(soup)

    if not name:
        return None

    # 🌐 Real company website.
    website = _extract_company_website(soup)

    # 📝 Company description.
    description = _extract_description(soup)

    # 📍 Location.
    location = _extract_labeled_value(
        soup,
        "Location",
    )

    # 🎓 YC batch.
    yc_batch = _extract_batch(soup)

    # 👥 Team size.
    employee_count = _extract_employee_count(soup)

    # ✅ Company status.
    page_text = soup.get_text(" ", strip=True)

    is_active = "Active" in page_text

    # 💼 YC exposes the jobs page under /jobs.
    jobs_url = f"{yc_url.rstrip('/')}/jobs"

    # 3️⃣ Check actual jobs.
    job_links, remote_friendly = await _inspect_jobs_page(
        client,
        jobs_url,
    )

    # 💼 Having actual job links is our hiring signal.
    is_hiring = len(job_links) > 0

    return YCCompany(
        name=name,
        yc_url=yc_url,
        website=website,
        description=description,
        location=location,
        yc_batch=yc_batch,
        employee_count=employee_count,
        is_active=is_active,
        is_hiring=is_hiring,
        remote_friendly=remote_friendly,
        jobs_url=jobs_url,
    )


def _extract_name(soup: BeautifulSoup) -> str | None:
    """🏷️ Extract company name."""

    heading = soup.find("h1")

    if not heading:
        return None

    return heading.get_text(
        " ",
        strip=True,
    )


def _extract_company_website(
    soup: BeautifulSoup,
) -> str | None:
    """🌐 Find the company's real website."""

    for link in soup.find_all("a", href=True):
        href = str(link["href"])

        if not href.startswith("http"):
            continue

        if "ycombinator.com" in href:
            continue

        # 🚫 Ignore common social links.
        if any(
            domain in href
            for domain in (
                "linkedin.com",
                "twitter.com",
                "x.com",
                "facebook.com",
            )
        ):
            continue

        return href

    return None


def _extract_description(
    soup: BeautifulSoup,
) -> str | None:
    """📝 Extract YC's company description."""

    meta = soup.find(
        "meta",
        attrs={"name": "description"},
    )

    if isinstance(meta, Tag):
        content = meta.get("content")

        if content:
            return str(content).strip()

    return None


def _extract_labeled_value(
    soup: BeautifulSoup,
    label: str,
) -> str | None:
    """🏷️ Extract a value such as Location or Team Size."""

    text = soup.get_text(
        " ",
        strip=True,
    )

    pattern = (
        rf"{label}\s*:\s*(.+?)(?=\s+(?:Founded|Batch|Team Size|Status|Location)\s*:|$)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return match.group(1).strip()


def _extract_batch(
    soup: BeautifulSoup,
) -> str | None:
    """🎓 Extract YC batch."""

    text = soup.get_text(
        " ",
        strip=True,
    )

    # Examples:
    # Winter 2023
    # Fall 2025
    # W23
    # S22
    match = re.search(
        r"(?:Winter|Spring|Summer|Fall)\s+\d{4}",
        text,
        flags=re.IGNORECASE,
    )

    if match:
        return match.group(0)

    match = re.search(
        r"\b[WSF]\d{2}\b",
        text,
    )

    if match:
        return match.group(0)

    return None


def _extract_employee_count(
    soup: BeautifulSoup,
) -> int | None:
    """👥 Extract current team size."""

    text = soup.get_text(
        " ",
        strip=True,
    )

    match = re.search(
        r"Team Size\s*:\s*([\d,]+)",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return None

    return int(match.group(1).replace(",", ""))


async def _inspect_jobs_page(
    client: httpx.AsyncClient,
    jobs_url: str,
) -> tuple[list[str], bool]:
    """💼 Inspect company jobs and detect remote hiring."""

    response = await client.get(jobs_url)

    if response.status_code == 404:
        return [], False

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser",
    )

    job_urls: set[str] = set()
    remote_friendly = False

    for link in soup.find_all("a", href=True):
        href = str(link["href"])

        if "/jobs/" not in href:
            continue

        full_url = urljoin(
            YC_BASE_URL,
            href,
        )

        job_urls.add(full_url)

        # 📍 Remote hiring signal.
        text = link.get_text(
            " ",
            strip=True,
        ).lower()

        if "remote" in text:
            remote_friendly = True

    return list(job_urls), remote_friendly
