import json  # 🔄 Convert data to JSON
import logging  # 📝 Write logs

from groq.types.chat import (
    ChatCompletionAssistantMessageParam,  # 🤖 Assistant message
    ChatCompletionMessageParam,  # 💬 General message
    ChatCompletionMessageToolCallParam,  # 🔧 Tool call
    ChatCompletionSystemMessageParam,  # 🧠 System message
    ChatCompletionToolMessageParam,  # 🛠️ Tool response
    ChatCompletionUserMessageParam,  # 👤 User message
)
from sqlalchemy.ext.asyncio import AsyncSession  # 🗄️ Database session

from app.agent.prompt.v1_prompt import SYSTEM_PROMPT  # 🧠 AI instructions
from app.agent.tools.jobs import (
    JobRecommendation,  # 💼 Job recommendation
    get_my_recommendations,  # 🔎 Get user's jobs
)
from app.agent.tools.tool_list import RECOMMENDATION_TOOLS  # 🛠️ AI tools
from app.agent.types import AgentResult  # 📦 Agent result
from app.core.config import get_settings  # ⚙️ App settings
from app.llm.client import client  # 🤖 Groq client

# 📝 Create logger
logger = logging.getLogger(__name__)

# ⚙️ Load settings
settings = get_settings()


# 📨 Build the first AI conversation
def build_messages(
    message: str,
) -> list[ChatCompletionMessageParam]:
    # 🧠 Add system instructions
    system_message: ChatCompletionSystemMessageParam = {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }

    # 👤 Add user message
    user_message: ChatCompletionUserMessageParam = {
        "role": "user",
        "content": message,
    }

    # 📦 Return messages
    return [
        system_message,
        user_message,
    ]


# 🤖 Ask Groq for the first response
async def get_initial_response(
    messages: list[ChatCompletionMessageParam],
):
    # 📤 Send conversation to Groq
    return await client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        tools=RECOMMENDATION_TOOLS,
        tool_choice="auto",
        temperature=0.3,
    )


# 💬 Create a normal text result
def create_text_result(
    content: str | None,
) -> AgentResult:
    # ❌ Make sure AI returned text
    if not content:
        raise ValueError("LLM returned an empty response")

    # 📦 Return text result
    return AgentResult(
        type="text",
        content=content,
    )


# 🔧 Add AI tool request to the conversation
def add_tool_request(
    messages: list[ChatCompletionMessageParam],
    assistant_message,
) -> None:
    # 🔄 Convert tool calls to message format
    tool_calls: list[ChatCompletionMessageToolCallParam] = [
        {
            "id": tool_call.id,
            "type": "function",
            "function": {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments,
            },
        }
        for tool_call in assistant_message.tool_calls
    ]

    # 🤖 Create assistant tool message
    assistant_message_param: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "content": assistant_message.content or "",
        "tool_calls": tool_calls,
    }

    # 📦 Add it to conversation
    messages.append(assistant_message_param)


# 🔧 Run the AI's requested tools
async def handle_tool_calls(
    messages: list[ChatCompletionMessageParam],
    tool_calls,
    db: AsyncSession,
    user_id: str,
) -> list[JobRecommendation]:
    # 💼 Store job recommendations
    jobs: list[JobRecommendation] = []

    # 🔄 Process each tool call
    for tool_call in tool_calls:
        # 🚫 Reject unknown tools
        if tool_call.function.name != "get_my_recommendations":
            raise ValueError(f"Unsupported agent tool: {tool_call.function.name}")

        # 🔎 Get jobs for authenticated user
        # 🔐 user_id comes from authentication
        jobs = await get_my_recommendations(
            db=db,
            user_id=user_id,
        )

        # 📦 Build tool response
        tool_message: ChatCompletionToolMessageParam = {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(
                jobs,
                ensure_ascii=False,
            ),
        }

        # ➕ Add tool result to conversation
        messages.append(tool_message)

    # 📤 Return jobs
    return jobs


# 🤖 Ask Groq for the final response
async def get_final_response(
    messages: list[ChatCompletionMessageParam],
) -> str:
    # 📤 Send tool results to Groq
    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=messages,
        temperature=0.3,
    )

    # 📦 Get final text
    content = response.choices[0].message.content

    # ❌ Make sure AI returned text
    if not content:
        raise ValueError("LLM returned an empty response")

    # 📤 Return final text
    return content


# 🤖 Run L and coordinate the AI workflow
async def run_agent(
    message: str,
    user_id: str,
    db: AsyncSession,
) -> AgentResult:
    # 📝 Log incoming request
    logger.info(
        "agent_request_received user_id=%s",
        user_id,
    )

    # 📨 Build conversation
    messages = build_messages(message)

    # 🤖 Ask AI what to do
    response = await get_initial_response(messages)

    # 📦 Get AI response
    assistant_message = response.choices[0].message

    # 💬 AI answered without a tool
    if not assistant_message.tool_calls:
        result = create_text_result(
            assistant_message.content,
        )

        # 📝 Log normal response
        logger.info(
            "agent_response_created user_id=%s",
            user_id,
        )

        return result

    # 🔧 Add AI tool request
    add_tool_request(
        messages=messages,
        assistant_message=assistant_message,
    )

    # 🛠️ Run requested tools
    jobs = await handle_tool_calls(
        messages=messages,
        tool_calls=assistant_message.tool_calls,
        db=db,
        user_id=user_id,
    )

    # 🤖 Get final AI response
    content = await get_final_response(messages)

    # 📝 Log tool response
    logger.info(
        "agent_tool_response_created user_id=%s",
        user_id,
    )

    # 📤 Return jobs and AI response
    return AgentResult(
        type="jobs",
        content=content,
        jobs=jobs,
    )
