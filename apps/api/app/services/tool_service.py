import time
from dataclasses import dataclass
from typing import Any, Protocol
from uuid import uuid4

from app.services.tool_audit_service import tool_audit_service
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
    trace_id: str | None = None
    latency_ms: int = 0
    audit_id: int | None = None


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

    async def run(self, name: str, args: dict[str, Any], agent_id: int | None = None, trace_id: str | None = None) -> ToolCallRecord:
        trace_id = trace_id or f"trace-{uuid4().hex[:12]}"
        started = time.perf_counter()
        tool = self._tools.get(name)
        if tool is None:
            latency_ms = int((time.perf_counter() - started) * 1000)
            audit = tool_audit_service.record(trace_id, name, args, {}, "failed", latency_ms, agent_id, "Tool not found")
            return ToolCallRecord(tool_name=name, input=args, output={}, status="failed", error_message="Tool not found", trace_id=trace_id, latency_ms=latency_ms, audit_id=int(audit["id"]))
        try:
            output = await tool.run(args)
            latency_ms = int((time.perf_counter() - started) * 1000)
            audit = tool_audit_service.record(trace_id, name, args, output, "success", latency_ms, agent_id)
            return ToolCallRecord(tool_name=name, input=args, output=output, trace_id=trace_id, latency_ms=latency_ms, audit_id=int(audit["id"]))
        except Exception as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            audit = tool_audit_service.record(trace_id, name, args, {}, "failed", latency_ms, agent_id, str(exc))
            return ToolCallRecord(tool_name=name, input=args, output={}, status="failed", error_message=str(exc), trace_id=trace_id, latency_ms=latency_ms, audit_id=int(audit["id"]))


tool_registry = ToolRegistry()
tool_registry.register(KnowledgeSearchTool())
tool_registry.register(CalculatorTool())
tool_registry.register(SQLQueryTool())
tool_registry.register(HTTPRequestTool())
