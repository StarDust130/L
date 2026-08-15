from typing import TypedDict

import httpx
from tavily import TavilyClient

from app.core.config import get_settings

settings = get_settings()


class WebSearchResult(TypedDict):
    """🌐 Clean web-search result returned to L."""

    title: str
    url: str
    content: str
    score: float


async def search_web(
    query: str,
) -> list[WebSearchResult]:
    """🔎 Search the web for current information."""

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
                "content": str(item.get("content", "")),
                "score": float(item.get("score", 0)),
            }
        )

    return results


async def fetch_page(url: str) -> str:
    """
    🌐 Fetch a real webpage.

    Search tells L:
        "This page looks interesting."

    fetch_page gives L:
        "Here is the actual page so you can investigate it."
    """

    try:
        async with httpx.AsyncClient(
            timeout=20,
            follow_redirects=True,
            headers={
                # 🕵️ Identify our crawler politely.
                "User-Agent": "L-Career-Agent/1.0",
            },
        ) as client:
            response = await client.get(url)

            response.raise_for_status()

            # 🛡️ Prevent gigantic pages from entering the LLM.
            return response.text[:30_000]

    except httpx.HTTPError as exc:
        return f"PAGE_FETCH_FAILED: {exc}"
