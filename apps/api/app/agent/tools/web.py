from typing import TypedDict
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup, Tag
from tavily import TavilyClient

from app.core.config import get_settings

settings = get_settings()


class WebSearchResult(TypedDict):
    """Clean web-search result returned to L."""

    title: str
    url: str
    content: str
    score: float


async def search_web(
    query: str,
) -> list[WebSearchResult] | dict[str, str]:
    """Search the web for current information."""

    query = query.strip()

    # Prevent invalid Tavily queries such as:
    # "site:wellfound.com"
    if not query:
        return {
            "error": "Search query cannot be empty.",
        }

    # Query must contain real search words.
    words = [
        word
        for word in query.split()
        if not word.startswith(("site:", "intitle:", "inurl:"))
    ]

    if not words:
        return {
            "error": (
                "Invalid search query. "
                "Use real search terms, not only search operators. "
                'Example: "junior FastAPI remote jobs site:wellfound.com"'
            ),
        }

    client = TavilyClient(
        api_key=settings.tavily_api_key,
    )

    response = client.search(
        query=query,
        search_depth="basic",
        max_results=5,
        include_answer=False,
        include_raw_content=False,
    )

    results: list[WebSearchResult] = []

    for item in response.get("results", []):
        results.append(
            {
                "title": str(item.get("title", "")),
                "url": str(item.get("url", "")),
                "content": str(item.get("content", ""))[:1200],
                "score": float(item.get("score", 0)),
            }
        )

    return results


_NOISE_TAGS = (
    "script",
    "style",
    "noscript",
    "svg",
    "nav",
    "footer",
    "header",
    "form",
    "aside",
    "iframe",
    "canvas",
    "template",
)

_NOISE_MARKERS = (
    "cookie",
    "consent",
    "popup",
    "modal",
    "newsletter",
    "advert",
    "advertisement",
    "tracking",
    "tracker",
    "banner",
    "breadcrumb",
    "social-share",
)


def _is_noise_element(element: Tag) -> bool:
    """
    Safely detect common non-content containers.
    """

    attrs = element.attrs or {}

    class_value = attrs.get("class")

    if isinstance(class_value, (list, tuple)):
        classes = " ".join(str(value) for value in class_value).lower()
    else:
        classes = str(class_value or "").lower()

    element_id = str(attrs.get("id") or "").lower()

    marker = f"{classes} {element_id}"

    return any(noise in marker for noise in _NOISE_MARKERS)


def _extract_links(
    root: Tag,
    base_url: str,
) -> list[str]:
    """
    Extract useful absolute links without crashing
    on malformed HTML.
    """

    links: list[str] = []

    for anchor in root.find_all("a"):
        if not isinstance(anchor, Tag):
            continue

        attrs = anchor.attrs or {}

        href_value = attrs.get("href")

        if not isinstance(href_value, str):
            continue

        href = href_value.strip()

        if not href:
            continue

        absolute_url = urljoin(
            base_url,
            href,
        )

        if not absolute_url.startswith(("http://", "https://")):
            continue

        link_text = anchor.get_text(
            " ",
            strip=True,
        )

        if not link_text:
            continue

        links.append(f"[LINK] {link_text} -> {absolute_url}")

    # Remove duplicates while preserving order.
    return list(dict.fromkeys(links))


async def fetch_page(url: str) -> str:
    """
    Fetch a webpage and return compact readable text
    plus useful links.
    """

    if not isinstance(url, str) or not url.strip():
        return "PAGE_FETCH_FAILED: Invalid URL."

    url = url.strip()

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/151.0 Safari/537.36 "
                    "L-Career-Agent/1.0"
                ),
                "Accept": (
                    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

        # Some pages return non-HTML content successfully.
        content_type = response.headers.get(
            "content-type",
            "",
        ).lower()

        if "html" not in content_type and "xhtml" not in content_type:
            return f"PAGE_FETCH_FAILED: Unsupported content type: {content_type}"

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove obvious noise tags.
        for element in soup.find_all(_NOISE_TAGS):
            element.decompose()

        # Remove cookie/popup/advert containers safely.
        for element in soup.find_all(["div", "section", "aside"]):
            if not isinstance(element, Tag):
                continue

            if _is_noise_element(element):
                element.decompose()

        # Prefer actual page content.
        main = soup.find("main") or soup.find("article") or soup.find("body")

        if not isinstance(main, Tag):
            return "PAGE_FETCH_FAILED: No readable page content found."

        # Preserve links BEFORE converting HTML to text.
        links = _extract_links(
            main,
            url,
        )

        text = main.get_text(
            separator=" ",
            strip=True,
        )

        # Normalize whitespace.
        text = " ".join(text.split())

        if not text:
            return "PAGE_FETCH_FAILED: Page contains no useful text."

        # Keep useful information dense.
        useful_links = "\n".join(links[:500])

        result = f"PAGE TEXT:\n{text[:40000]}\n\nUSEFUL LINKS:\n{useful_links}"

        return result[:50000]

    except httpx.HTTPStatusError as exc:
        return f"PAGE_FETCH_FAILED: HTTP {exc.response.status_code}"

    except httpx.RequestError as exc:
        return f"PAGE_FETCH_FAILED: Request error: {exc}"

    except Exception as exc:
        return f"PAGE_FETCH_FAILED: Unexpected error: {exc}"
