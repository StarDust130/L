from collections.abc import Awaitable, Callable
from typing import Any

from groq.types.chat import ChatCompletionToolParam

from app.agent.tools.jobs import get_my_recommendations
from app.agent.tools.web import fetch_page, search_web

# 🤖 Tools exposed to the LLM.
TOOL_SCHEMAS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_my_recommendations",
            "description": (
                "Get the authenticated user's best job recommendations. "
                "Use this when the user asks for their jobs, "
                "recommended jobs, best matches, or matching jobs."
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
                "Search the internet for real, current information. "
                "Use this when the user asks to find new jobs, "
                "companies, career opportunities, or other information "
                "that may not exist in the database."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": ("A precise web search query."),
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
                "Open and inspect a webpage when a search result "
                "looks useful. Use this to investigate a company, "
                "career page, job listing, funding announcement, "
                "or other relevant source."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The exact webpage URL to inspect.",
                    },
                },
                "required": ["url"],
            },
        },
    },
]


# 🔧 Real Python functions executed by our backend.
TOOL_FUNCTIONS: dict[
    str,
    Callable[..., Awaitable[Any]],
] = {
    "get_my_recommendations": get_my_recommendations,
    "search_web": search_web,
    "fetch_page": fetch_page,
}
