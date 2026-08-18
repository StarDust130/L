from collections.abc import Awaitable, Callable
from typing import Any

from groq.types.chat import ChatCompletionToolParam

from app.agent.memory.memory_service import save_memory
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
                "Search the web for NEW or CURRENT information only when the user "
                "actually asks you to find, search, discover, check, look up, or verify "
                "something external. "
                "IMPORTANT: Do NOT use this tool when the user is merely telling you "
                "a preference, opinion, goal, or fact about themselves. "
                "For example, 'I love remote startup jobs' is a memory statement, "
                "not a search request. "
                "Use search_web for requests like 'Find remote startup jobs'. "
                "The query must contain real search terms."
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
    {
        "type": "function",
        "function": {
            "name": "save_memory",
            "description": (
                "Save useful long-term career information about the user. "
                "Use this when the user naturally expresses a stable preference, "
                "goal, like, dislike, or career fact that could improve future "
                "job matching. The user does NOT need to say 'remember'. "
                "IMPORTANT: A preference statement should normally use this tool "
                "and should NOT trigger web search. "
                "Do not save casual conversation, jokes, temporary requests, "
                "or unrelated personal information. "
                "Examples: "
                '"I prefer remote jobs"; '
                '"I like startups with fewer than 10 people"; '
                '"I love FastAPI"; '
                '"I don\'t want fintech jobs"; '
                '"I like companies similar to Stripe".'
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": [
                            "job_preferences",
                            "company_preferences",
                            "technology_preferences",
                            "location_preferences",
                            "role_preferences",
                            "likes",
                            "dislikes",
                            "career_goals",
                            "career_facts",
                        ],
                    },
                    "key": {
                        "type": "string",
                        "description": (
                            "The specific thing to remember. "
                            "Examples: work_mode, company_size, preferred_stack, "
                            "preferred_company, disliked_industry."
                        ),
                    },
                    "value": {
                        "type": "string",
                        "description": (
                            "The user's actual preference or fact. "
                            "Example: 'remote worldwide' or 'under 10 employees'."
                        ),
                    },
                },
                "required": ["category", "key", "value"],
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
    "save_memory": save_memory,
}
