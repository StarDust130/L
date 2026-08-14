import json
import logging

from groq.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionToolMessageParam,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.tool_list import (
    TOOL_FUNCTIONS,
    TOOL_SCHEMAS,
)
from app.core.config import get_settings
from app.llm.client import client

logger = logging.getLogger(__name__)
settings = get_settings()


SYSTEM_PROMPT = """
You are L, a private career intelligence assistant.

Be concise, useful, and direct.

When the user asks for their jobs, recommended jobs,
best matches, or matching jobs, use the
get_my_recommendations tool.

Never invent jobs, companies, scores, or application links.

If a tool returns no results, honestly say that no
recommendations were found.

Do not ask the user for their user ID.
"""

MAX_ITERATIONS = 5


async def run_agent(
    db: AsyncSession,
    message: str,
    user_id: str,
) -> str:
    """🧠 Run the L agent loop."""

    # 1️⃣ Start conversation history
    messages: list[ChatCompletionMessageParam] = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    # 2️⃣ Run agent loop
    for iteration in range(MAX_ITERATIONS):
        logger.info(
            "🤖 agent_iteration=%s user_id=%s",
            iteration + 1,
            user_id,
        )

        # 3️⃣ Send messages to Groq
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
            temperature=0.2,
        )

        # 4️⃣ Get assistant response
        assistant = response.choices[0].message

        # 5️⃣ Return final answer if no tool is needed
        if not assistant.tool_calls:
            return assistant.content or "I couldn't generate a response."

        # 6️⃣ Convert assistant response into typed message
        assistant_message: ChatCompletionAssistantMessageParam = {
            "role": "assistant",
            "content": assistant.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in assistant.tool_calls
            ],
        }

        # 7️⃣ Add assistant message to history
        messages.append(assistant_message)

        # 8️⃣ Execute each requested tool
        for tool_call in assistant.tool_calls:
            tool_name = tool_call.function.name

            # 9️⃣ Find tool function
            tool = TOOL_FUNCTIONS.get(tool_name)

            # 🔟 Handle missing tool
            if tool is None:
                tool_result = f"Tool '{tool_name}' is not available."

            else:
                try:
                    # 1️⃣1️⃣ Parse tool arguments
                    arguments = json.loads(tool_call.function.arguments)

                    # 1️⃣2️⃣ Keep user_id controlled by backend
                    if tool_name == "get_my_recommendations":
                        result = await tool(
                            db=db,
                            user_id=user_id,
                        )
                    else:
                        result = await tool(**arguments)

                    # 1️⃣3️⃣ Convert result to JSON
                    tool_result = json.dumps(
                        result,
                        default=str,
                    )

                except Exception:
                    # 1️⃣4️⃣ Log tool error
                    logger.exception(
                        "❌ Tool failed: %s",
                        tool_name,
                    )

                    tool_result = f"Tool '{tool_name}' failed."

            # 1️⃣5️⃣ Build typed tool message
            tool_message: ChatCompletionToolMessageParam = {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            }

            # 1️⃣6️⃣ Add tool result to history
            messages.append(tool_message)

    # 1️⃣7️⃣ Stop after maximum iterations
    logger.warning(
        "🛑 Agent reached max iterations.",
    )

    return "I couldn't finish that request right now. Please try again."
