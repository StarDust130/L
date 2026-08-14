from collections.abc import Awaitable, Callable

ToolFunction = Callable[..., Awaitable[str]]


TOOL_FUNCTIONS: dict[str, ToolFunction] = {}


def register_tool(
    name: str,
    function: ToolFunction,
) -> None:
    """🔧 Register a tool that the agent is allowed to use."""

    TOOL_FUNCTIONS[name] = function
