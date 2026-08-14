from collections.abc import Awaitable, Callable
from typing import Any

from groq.types.chat import ChatCompletionToolParam

from app.agent.tools.jobs import get_my_recommendations

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
]


# 🔧 Real Python functions executed by our backend.
TOOL_FUNCTIONS: dict[
    str,
    Callable[..., Awaitable[Any]],
] = {
    "get_my_recommendations": get_my_recommendations,
}
