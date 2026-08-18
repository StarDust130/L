import json
from typing import Any

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


MAX_ITERATIONS = 7


# ! MAIN AGENT LOOP 🔞
async def run_agent(
    db: AsyncSession,
    message: str,
    user_id: str,
) -> AgentResult:
    """
    Simple Gemini agent loop.

    User
      ↓
    Gemini
      ↓
    Text → finish
      ↓
    Tool → run tool
      ↓
    Send tool result to Gemini
      ↓
    Repeat
    """

    user_context = await build_user_context(
        db=db,
        user_id=user_id,
    )

    contents: list[types.Content] = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=f"""
    USER CONTEXT:
    {json.dumps(user_context, default=str)}

    USER MESSAGE:
    {message}
    """,
                ),
            ],
        )
    ]

    tools = get_gemini_tools()

    for _ in range(MAX_ITERATIONS):
        # ------------------------------------------------
        # Ask Gemini
        # ------------------------------------------------
        try:
            response = await gemini_client.aio.models.generate_content(
                model=settings.gemini_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    tools=tools,
                    temperature=0.2,
                    automatic_function_calling=(
                        types.AutomaticFunctionCallingConfig(
                            disable=True,
                        )
                    ),
                ),
            )

        except APIError as error:
            print(f"Gemini API error: {error}")

            return AgentResult(
                type="text",
                content="Sorry, I couldn't finish that request right now.",
            )

        # ------------------------------------------------
        # No tool call = Gemini is finished
        # ------------------------------------------------
        function_calls = response.function_calls

        if not function_calls:
            return AgentResult(
                type="text",
                content=response.text or "",
            )

        # ------------------------------------------------
        # Get Gemini's message
        # ------------------------------------------------
        candidates = response.candidates or []

        if not candidates:
            return AgentResult(
                type="text",
                content="Gemini returned no response.",
            )

        assistant_content = candidates[0].content

        if assistant_content is None:
            return AgentResult(
                type="text",
                content="Gemini returned an invalid response.",
            )

        contents.append(assistant_content)

        # ------------------------------------------------
        # Run requested tools
        # ------------------------------------------------
        tool_parts: list[types.Part] = []

        for function_call in function_calls:
            tool_name = function_call.name

            if not tool_name:
                return AgentResult(
                    type="text",
                    content="Gemini returned an invalid tool call.",
                )

            arguments = dict(function_call.args or {})

            # If this tool crashes, the error stops the agent.
            result = await execute_tool(
                tool_name=tool_name,
                arguments=arguments,
                db=db,
                user_id=user_id,
            )

            tool_parts.append(
                types.Part.from_function_response(
                    name=tool_name,
                    response={
                        "output": result,
                    },
                )
            )

        # ------------------------------------------------
        # Send tool results back to Gemini
        # ------------------------------------------------
        contents.append(
            types.Content(
                role="user",
                parts=tool_parts,
            )
        )

    # ------------------------------------------------
    # Maximum iterations reached
    # ------------------------------------------------
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
    Run the tool Gemini requested.
    """

    tool = TOOL_FUNCTIONS.get(tool_name)

    if tool is None:
        return f"Tool '{tool_name}' does not exist."

    if tool_name == "get_my_recommendations":
        result = await tool(
            db=db,
            user_id=user_id,
        )

    elif tool_name == "save_source":
        result = await tool(
            db=db,
            **arguments,
        )

    else:
        result = await tool(**arguments)

    return json.dumps(result, default=str)


def get_gemini_tools() -> list[types.Tool]:
    """
    Convert our existing tool schemas into Gemini's format.
    """

    functions = []

    for schema in TOOL_SCHEMAS:
        function = schema.get("function")

        if not isinstance(function, dict):
            continue

        functions.append(
            types.FunctionDeclaration(
                name=function["name"],
                description=function.get("description", ""),
                parameters_json_schema=function.get(
                    "parameters",
                    {"type": "object"},
                ),
            )
        )

    return [
        types.Tool(
            function_declarations=functions,
        )
    ]
