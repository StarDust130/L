from typing import TypedDict

import httpx
from bs4 import BeautifulSoup
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


async def fetch_page(url: str) -> str:
    """Fetch and clean a webpage."""

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={
                "User-Agent": "L-Career-Agent/1.0",
            },
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            # Remove obvious page noise.
            for element in soup(["script", "style", "noscript", "svg"]):
                element.decompose()

            # Prefer main content.
            main = soup.find("main") or soup.body

            if not main:
                return "PAGE_FETCH_FAILED: No readable page content found."

            text = main.get_text(
                separator=" ",
                strip=True,
            )

            # Prevent huge pages from entering Gemini.
            return text[:8_000]

    except httpx.HTTPError as exc:
        return f"PAGE_FETCH_FAILED: {exc}"
