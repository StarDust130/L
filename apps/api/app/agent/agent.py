import json
import logging
from typing import Any, cast

from google.genai import types
from google.genai.errors import APIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.memory.context import build_user_context
from app.agent.prompt.v1_prompt import SYSTEM_PROMPT
from app.agent.tools.tool_list import TOOL_FUNCTIONS, TOOL_SCHEMAS
from app.agent.types import AgentResult
from app.core.config import get_settings
from app.llm.client import gemini_client

settings = get_settings()
logger = logging.getLogger(__name__)


MAX_ITERATIONS = 10


# ! MAIN AGENT LOOP 🔞
async def run_agent(
    db: AsyncSession,
    message: str,
    user_id: str,
) -> AgentResult:
    """Run the Gemini agent loop."""

    logger.info(
        "🤖 Agent started | user=%s | message=%s",
        user_id,
        message,
    )

    user_context = await build_user_context(
        db=db,
        user_id=user_id,
    )

    logger.info(
        "🧠 User context loaded | profile=%s | memory=%s",
        bool(user_context.get("profile")),
        bool(user_context.get("memory")),
    )

    contents: list[types.Content] = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=(
                        "USER CONTEXT:\n"
                        f"{json.dumps(user_context, default=str)}\n\n"
                        "USER MESSAGE:\n"
                        f"{message}"
                    ),
                ),
            ],
        ),
    ]

    tools = get_gemini_tools()

    tool_names = [
        declaration.name
        for tool in tools
        for declaration in (tool.function_declarations or [])
        if declaration.name
    ]

    logger.info(
        "🔧 Tools available | %s",
        tool_names,
    )

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info(
            "🔄 Agent iteration %d/%d",
            iteration,
            MAX_ITERATIONS,
        )

        tool_config = None

        try:
            response = await gemini_client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=tools,
                    tool_config=tool_config,
                    automatic_function_calling=(
                        types.AutomaticFunctionCallingConfig(
                            disable=True,
                        )
                    ),
                ),
            )

        except APIError as error:
            logger.error(
                "❌ Gemini API error | iteration=%d | error=%s",
                iteration,
                error,
            )

            return AgentResult(
                type="text",
                content="Sorry, I couldn't finish that request right now.",
            )

        function_calls = response.function_calls or []

        # Gemini has finished.
        if not function_calls:
            logger.info(
                "✅ Gemini finished | iteration=%d | text=%s",
                iteration,
                (response.text or "")[:300],
            )

            return AgentResult(
                type="text",
                content=response.text or "",
            )

        logger.info(
            "🛠️ Gemini requested %d tool call(s)",
            len(function_calls),
        )

        candidates = response.candidates or []

        if not candidates:
            logger.error("❌ Gemini returned no candidates")

            return AgentResult(
                type="text",
                content="Gemini returned no response.",
            )

        assistant_content = candidates[0].content

        if assistant_content is None:
            logger.error("❌ Gemini returned empty assistant content")

            return AgentResult(
                type="text",
                content="Gemini returned an invalid response.",
            )

        contents.append(assistant_content)

        tool_parts: list[types.Part] = []

        for function_call in function_calls:
            tool_name = function_call.name

            if not tool_name:
                logger.error(
                    "❌ Gemini returned a tool call without a name",
                )

                return AgentResult(
                    type="text",
                    content="Gemini returned an invalid tool call.",
                )

            arguments = dict(function_call.args or {})

            logger.info(
                "🔧 Tool requested | name=%s | args=%s",
                tool_name,
                arguments,
            )

            result = await execute_tool(
                tool_name=tool_name,
                arguments=arguments,
                db=db,
                user_id=user_id,
            )

            logger.info(
                "✅ Tool finished | name=%s | result=%s",
                tool_name,
                result[:500],
            )

            tool_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={
                        "output": result,
                    },
                ),
            )

        contents.append(
            types.Content(
                role="user",
                parts=tool_parts,
            ),
        )

        logger.info(
            "📨 Tool results sent back to Gemini | iteration=%d",
            iteration,
        )

    logger.warning(
        "⚠️ Maximum iterations reached | max=%d",
        MAX_ITERATIONS,
    )

    return AgentResult(
        type="text",
        content="I couldn't finish that request.",
    )


# !  TOOL EXECUTION FUNCTION 🔧
async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    db: AsyncSession,
    user_id: str,
) -> str:
    """
    Execute an L tool with the correct backend context.
    """

    tool = TOOL_FUNCTIONS.get(tool_name)

    if tool is None:
        return f"Tool '{tool_name}' does not exist."

    if tool_name == "get_my_recommendations":
        result = await tool(
            db=db,
            user_id=user_id,
        )

    elif tool_name == "get_known_sources":
        result = await tool(
            db=db,
        )

    elif tool_name == "save_source":
        result = await tool(
            db=db,
            **arguments,
        )

    elif tool_name == "save_memory":
        result = await tool(
            db=db,
            user_id=user_id,
            memory_data={
                arguments["category"]: {
                    arguments["key"]: arguments["value"],
                }
            },
        )

    else:
        result = await tool(**arguments)

    return json.dumps(
        result,
        default=str,
    )

def get_gemini_tools() -> list[types.Tool]:
    """Convert our existing tool schemas into Gemini's format."""

    functions: list[types.FunctionDeclaration] = []

    for schema in TOOL_SCHEMAS:
        function = schema.get("function")

        if not isinstance(function, dict):
            continue

        name = function.get("name")

        if not isinstance(name, str) or not name:
            continue

        description = function.get("description", "")

        if not isinstance(description, str):
            description = str(description)

        parameters = function.get("parameters")

        if parameters is None:
            parameters_json_schema: dict[str, Any] = {
                "type": "object",
            }
        else:
            parameters_json_schema = cast(
                dict[str, Any],
                parameters,
            )

        functions.append(
            types.FunctionDeclaration(
                name=name,
                description=description,
                parameters_json_schema=parameters_json_schema,
            ),
        )

    logger.info(
        "🧰 Gemini tools loaded: %s",
        [function.name for function in functions],
    )

    return [
        types.Tool(
            function_declarations=functions,
        ),
    ]
