from dataclasses import dataclass
from typing import Any, Protocol

from app.services.tools import CalculatorTool, HTTPRequestTool, KnowledgeSearchTool, SQLQueryTool


class Tool(Protocol):
    name: str
    description: str
    args_schema: dict[str, object]

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        ...


@dataclass
class ToolCallRecord:
    tool_name: str
    input: dict[str, Any]
    output: dict[str, Any]
    status: str = "success"
    error_message: str | None = None


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def list_tools(self) -> list[dict[str, object]]:
        return [
            {"name": tool.name, "description": tool.description, "schema": tool.args_schema, "enabled": True}
            for tool in self._tools.values()
        ]

    async def run(self, name: str, args: dict[str, Any]) -> ToolCallRecord:
        tool = self._tools.get(name)
        if tool is None:
            return ToolCallRecord(tool_name=name, input=args, output={}, status="failed", error_message="Tool not found")
        try:
            output = await tool.run(args)
            return ToolCallRecord(tool_name=name, input=args, output=output)
        except Exception as exc:
            return ToolCallRecord(tool_name=name, input=args, output={}, status="failed", error_message=str(exc))


tool_registry = ToolRegistry()
tool_registry.register(KnowledgeSearchTool())
tool_registry.register(CalculatorTool())
tool_registry.register(SQLQueryTool())
tool_registry.register(HTTPRequestTool())
