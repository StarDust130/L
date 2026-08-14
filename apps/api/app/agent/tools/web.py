from typing import TypedDict

from tavily import TavilyClient

from app.core.config import get_settings

settings = get_settings()


class WebSearchResult(TypedDict):
    """🌐 Small, clean result returned to the agent."""

    title: str
    url: str
    content: str
    score: float


async def search_web(
    query: str,
) -> list[WebSearchResult]:
    """
    🔎 Search the web for information relevant to the user's request.

    The search provider does the web search.
    This function only normalizes the results into the small
    structure our agent needs.
    """

    # 🔐 API key stays on the backend.
    client = TavilyClient(
        api_key=settings.tavily_api_key,
    )

    # 💰 Basic search keeps the first version cheap.
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
