from dataclasses import dataclass
from typing import Protocol


class Tool(Protocol):
    name: str
    description: str
    args_schema: dict[str, object]

    async def run(self, args: dict[str, object]) -> dict[str, object]:
        ...


@dataclass
class ToolCallRecord:
    tool_name: str
    input: dict[str, object]
    output: dict[str, object]
    status: str = "success"


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> list[str]:
        return sorted(self._tools)


tool_registry = ToolRegistry()
