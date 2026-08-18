from collections.abc import Awaitable, Callable
from typing import Any

from groq.types.chat import ChatCompletionToolParam

from app.agent.tools.jobs import get_my_recommendations
from app.agent.tools.sources import get_known_sources, save_source

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
            "name": "get_known_sources",
            "description": (
                "Get trusted web sources that L already knows "
                "for discovering jobs and companies."
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
                "Save a genuinely useful web source for future "
                "job and company discovery. Only use this after "
                "investigating the source and determining that it "
                "contains valuable, relevant opportunities."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Human-readable source name.",
                    },
                    "url": {
                        "type": "string",
                        "description": "Canonical URL of the source.",
                    },
                    "source_type": {
                        "type": "string",
                        "description": (
                            "Type such as job_board, "
                            "company_directory, or career_platform."
                        ),
                    },
                    "description": {
                        "type": "string",
                        "description": "Why this source is useful.",
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


# 🔧 Real Python functions executed by our backend.
TOOL_FUNCTIONS: dict[
    str,
    Callable[..., Awaitable[Any]],
] = {
    "get_my_recommendations": get_my_recommendations,
    "get_known_sources": get_known_sources,
    "save_source": save_source,
}
