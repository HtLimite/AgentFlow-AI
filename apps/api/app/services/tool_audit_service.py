from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count
from typing import Any


@dataclass
class ToolAuditRecord:
    id: int
    trace_id: str
    agent_id: int | None
    tool_name: str
    input: dict[str, Any]
    output: dict[str, Any]
    status: str
    latency_ms: int
    error_message: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ToolAuditService:
    def __init__(self) -> None:
        self._ids = count(1)
        self._records: list[ToolAuditRecord] = []

    def record(
        self,
        trace_id: str,
        tool_name: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        status: str,
        latency_ms: int,
        agent_id: int | None = None,
        error_message: str | None = None,
    ) -> dict[str, Any]:
        item = ToolAuditRecord(
            id=next(self._ids),
            trace_id=trace_id,
            agent_id=agent_id,
            tool_name=tool_name,
            input=input_data,
            output=output_data,
            status=status,
            latency_ms=latency_ms,
            error_message=error_message,
        )
        self._records.append(item)
        return self._serialize(item)

    def list_records(self, limit: int = 50) -> list[dict[str, Any]]:
        return [self._serialize(item) for item in reversed(self._records[-limit:])]

    def get_record(self, record_id: int) -> dict[str, Any] | None:
        for item in self._records:
            if item.id == record_id:
                return self._serialize(item)
        return None

    def summary(self) -> dict[str, Any]:
        total = len(self._records)
        failed = sum(1 for item in self._records if item.status != "success")
        avg_latency = round(sum(item.latency_ms for item in self._records) / total, 2) if total else 0
        tool_counts: dict[str, int] = {}
        for item in self._records:
            tool_counts[item.tool_name] = tool_counts.get(item.tool_name, 0) + 1
        return {
            "total_calls": total,
            "failed_calls": failed,
            "success_rate": round((total - failed) / total, 4) if total else 1,
            "avg_latency_ms": avg_latency,
            "tool_counts": tool_counts,
            "source": "runtime_memory",
            "note": "Only real tool calls from the current process are listed. No demo audit rows are injected.",
        }

    def seed_if_empty(self) -> None:
        return None

    def _serialize(self, item: ToolAuditRecord) -> dict[str, Any]:
        return {
            "id": item.id,
            "trace_id": item.trace_id,
            "agent_id": item.agent_id,
            "tool_name": item.tool_name,
            "input": item.input,
            "output": item.output,
            "status": item.status,
            "latency_ms": item.latency_ms,
            "error_message": item.error_message,
            "created_at": item.created_at,
        }


tool_audit_service = ToolAuditService()
