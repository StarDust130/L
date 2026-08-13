from groq.types.chat import (
    ChatCompletionToolParam,  #  Tool definition type
)

# 🛠️ Tell the AI which tools it can use
RECOMMENDATION_TOOLS: list[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "get_my_recommendations",
            "description": (
                "Get the authenticated user's best job recommendations. "
                "Use this when the user asks to see their jobs, "
                "recommended jobs, best matches, or matching jobs."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    }
]
