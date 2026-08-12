import json
import logging

from groq.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionMessageToolCallParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionToolMessageParam,
    ChatCompletionToolParam,
    ChatCompletionUserMessageParam,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.tools.jobs import JobRecommendation, get_my_recommendations
from app.agent.types import AgentResult
from app.core.config import get_settings
from app.llm.client import client

logger = logging.getLogger(__name__)
settings = get_settings()

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

SYSTEM_PROMPT = (
    "You are L, a private career intelligence assistant. "
    "Be concise, useful, and direct. "
    "Format responses for Telegram mobile chat. "
    "Use short paragraphs and simple bullet points. "
    "Use emojis when useful. "
    "Do not use Markdown tables. "
    "Do not make up jobs or job information. "
    "When the user asks for their recommended jobs, use the "
    "get_my_recommendations tool. After the tool returns, give a short "
    "introductory response. If it returns an empty list, kindly say that "
    "there are no strong matches right now and suggest checking again later."
)


async def run_agent(
    message: str,
    user_id: str,
    db: AsyncSession,
) -> AgentResult:
    """Run L with access to the authenticated user's job recommendations."""

    logger.info("agent_request_received user_id=%s", user_id)

    system_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }
    user_message: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": message,
    }
    messages: list[ChatCompletionMessageParam] = [
        system_message,
        user_message,
    ]

    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        tools=RECOMMENDATION_TOOLS,
        tool_choice="auto",
        temperature=0.3,
    )

    assistant_message = response.choices[0].message
    tool_calls = assistant_message.tool_calls

    if not tool_calls:
        content = assistant_message.content
        if not content:
            raise ValueError("LLM returned an empty response")

        logger.info("agent_response_created user_id=%s", user_id)
        return AgentResult(type="text", content=content)

    assistant_tool_calls: list[ChatCompletionMessageToolCallParam] = [
        {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            },
        }
        for tool_call in tool_calls
    ]
    assistant_message_param: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "content": assistant_message.content or "",
        "tool_calls": assistant_tool_calls,
    }
    messages.append(assistant_message_param)

    jobs: list[JobRecommendation] = []
    for tool_call in tool_calls:
        if tool_call.function.name != "get_my_recommendations":
            raise ValueError(f"Unsupported agent tool: {tool_call.function.name}")

        # The user_id comes from Telegram authentication, never from tool input.
        jobs = await get_my_recommendations(db=db, user_id=user_id)
        tool_message: ChatCompletionToolMessageParam = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(jobs, ensure_ascii=False),
        }
        messages.append(tool_message)

    final_response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        temperature=0.3,
    )
    content = final_response.choices[0].message.content

    if not content:
        raise ValueError("LLM returned an empty response")

    logger.info("agent_tool_response_created user_id=%s", user_id)
    return AgentResult(type="jobs", content=content, jobs=jobs)
