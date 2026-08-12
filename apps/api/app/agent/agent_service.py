import json
import logging

from app.agent.tools.jobs import get_my_recommendations
from app.core.config import get_settings
from app.llm.client import client
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

settings = get_settings()


async def run_agent(
    message: str,
    user_id: str,
    db: AsyncSession,
) -> str:
    """🤖 Run L and allow it to use tools."""

    logger.info(
        "🤖 agent_request_received user_id=%s",
        user_id,
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_my_recommendations",
                "description": (
                    "Get the current user's best job recommendations. "
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

    messages = [
        {
            "role": "system",
            "content": (
                "You are L, a private career intelligence assistant. "
                "Be concise, useful, and direct. "
                "Format responses for Telegram mobile chat. "
                "Use short paragraphs and simple bullet points. "
                "Use emojis when useful. "
                "Do not use Markdown tables. "
                "Do not make up jobs or job information. "
                "When the user asks for their recommended jobs, "
                "use the get_my_recommendations tool."
            ),
        },
        {
            "role": "user",
            "content": message,
        },
    ]

    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.3,
    )

    assistant_message = response.choices[0].message

    # 🤔 LLM decided it needs a tool.
    if assistant_message.tool_calls:
        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments,
                        },
                    }
                    for tool_call in assistant_message.tool_calls
                ],
            }
        )

        for tool_call in assistant_message.tool_calls:
            if tool_call.function.name == "get_my_recommendations":
                jobs = await get_my_recommendations(
                    db=db,
                    user_id=user_id,
                )

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(jobs),
                    }
                )

        # 🧠 Give the tool result back to the LLM.
        final_response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=0.3,
        )

        content = final_response.choices[0].message.content

        if not content:
            raise ValueError("LLM returned an empty response")

        logger.info(
            "🤖 agent_tool_response_created user_id=%s",
            user_id,
        )

        return content

    # 💬 Normal conversation — no tool needed.
    content = assistant_message.content

    if not content:
        raise ValueError("LLM returned an empty response")

    logger.info(
        "🤖 agent_response_created user_id=%s",
        user_id,
    )

    return content
