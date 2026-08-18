from collections.abc import Awaitable, Callable
from typing import Any

from groq.types.chat import ChatCompletionToolParam

from app.agent.tools.jobs import get_my_recommendations
from app.agent.tools.sources import get_known_sources, save_source
from app.agent.tools.web import fetch_page, search_web

TOOL_SCHEMAS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_my_recommendations",
            "description": (
                "Get the user's existing job recommendations and best matches "
                "from our database. Use this when the user asks for their "
                "recommended jobs, saved matches, or current job matches. "
                "Do NOT use this to search the web for new jobs."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": (
                "Search the web for NEW and CURRENT information. "
                "Use this when you need to discover jobs, companies, "
                "job boards, career pages, or other relevant sources. "
                "The query must contain real search terms. "
                "You may use search operators together with real terms. "
                'Good example: "junior FastAPI remote jobs site:wellfound.com". '
                'Bad example: "site:wellfound.com". '
                "Do not use this when you already have the exact URL to inspect; "
                "use fetch_page instead. "
                "Do not repeat the same search unless the previous results "
                "were insufficient."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "A specific web search query containing real "
                            "keywords describing what you need to find."
                        ),
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page",
            "description": (
                "Read and inspect ONE specific webpage in detail. "
                "Use this when you already have a URL and need to verify "
                "its contents, such as a job posting, company page, "
                "career page, or job source. "
                "Do not use this to discover URLs; use search_web for discovery. "
                "Do not repeatedly fetch the same URL."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": (
                            "The exact webpage URL that should be inspected."
                        ),
                    },
                },
                "required": ["url"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_known_sources",
            "description": (
                "Get web sources that L already knows and has stored. "
                "Use this when you need to know which job boards, company "
                "directories, career platforms, or other sources are already "
                "known before discovering new ones. "
                "This helps avoid repeating work and saving duplicate sources."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_source",
            "description": (
                "Save a NEW, verified, genuinely useful web source for future "
                "job or company discovery. "
                "Only use this AFTER investigating the source with fetch_page "
                "and deciding that it provides valuable, relevant opportunities. "
                "Do NOT save random search results, generic pages, SEO content, "
                "low-quality aggregators, or sources already known."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Clear human-readable name of the source.",
                    },
                    "url": {
                        "type": "string",
                        "description": "Canonical URL of the source.",
                    },
                    "source_type": {
                        "type": "string",
                        "description": (
                            "The source category, for example "
                            "job_board, company_directory, "
                            "career_platform, or community."
                        ),
                    },
                    "description": {
                        "type": "string",
                        "description": (
                            "Short explanation of why this source is valuable "
                            "for discovering relevant jobs or companies."
                        ),
                    },
                },
                "required": [
                    "name",
                    "url",
                    "source_type",
                    "description",
                ],
            },
        },
    },
]


TOOL_FUNCTIONS: dict[
    str,
    Callable[..., Awaitable[Any]],
] = {
    "get_my_recommendations": get_my_recommendations,
    "search_web": search_web,
    "fetch_page": fetch_page,
    "get_known_sources": get_known_sources,
    "save_source": save_source,
}
