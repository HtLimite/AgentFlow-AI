from decimal import Decimal
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import ToolAuditLogModel


def _serialize(item: ToolAuditLogModel) -> dict[str, Any]:
    return {
        "id": item.id,
        "trace_id": item.trace_id,
        "agent_id": item.agent_id,
        "tool_name": item.tool_name,
        "input": item.input_json or {},
        "output": item.output_json or {},
        "status": item.status,
        "latency_ms": item.latency_ms,
        "error_message": item.error_message,
        "tenant_id": item.tenant_id,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "source": "database",
    }


class PersistentToolAuditService:
    async def record(self, session: AsyncSession, payload: dict[str, Any], tenant_id: int | None = 1) -> dict[str, Any]:
        item = ToolAuditLogModel(
            trace_id=str(payload.get("trace_id") or "unknown"),
            agent_id=payload.get("agent_id"),
            tool_name=str(payload.get("tool_name") or "unknown"),
            input_json=payload.get("input") if isinstance(payload.get("input"), dict) else {},
            output_json=payload.get("output") if isinstance(payload.get("output"), dict) else {},
            status=str(payload.get("status") or "success"),
            latency_ms=int(payload.get("latency_ms") or 0),
            error_message=payload.get("error_message"),
            tenant_id=tenant_id,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return _serialize(item)

    async def list_records(self, session: AsyncSession, limit: int = 50, tool_name: str | None = None, status: str | None = None) -> list[dict[str, Any]]:
        stmt = select(ToolAuditLogModel).order_by(desc(ToolAuditLogModel.id)).limit(limit)
        if tool_name:
            stmt = stmt.where(ToolAuditLogModel.tool_name == tool_name)
        if status:
            stmt = stmt.where(ToolAuditLogModel.status == status)
        result = await session.scalars(stmt)
        return [_serialize(item) for item in result.all()]

    async def get_record(self, session: AsyncSession, record_id: int) -> dict[str, Any] | None:
        item = await session.get(ToolAuditLogModel, record_id)
        return _serialize(item) if item else None

    async def summary(self, session: AsyncSession) -> dict[str, Any]:
        total = int(await session.scalar(select(func.count(ToolAuditLogModel.id))) or 0)
        failed = int(await session.scalar(select(func.count(ToolAuditLogModel.id)).where(ToolAuditLogModel.status != "success")) or 0)
        avg_latency = await session.scalar(select(func.avg(ToolAuditLogModel.latency_ms)))
        tool_rows = await session.execute(select(ToolAuditLogModel.tool_name, func.count(ToolAuditLogModel.id)).group_by(ToolAuditLogModel.tool_name))
        tool_counts = {tool: int(count) for tool, count in tool_rows.all()}
        avg_value = float(avg_latency) if isinstance(avg_latency, Decimal) else float(avg_latency or 0)
        return {
            "total_calls": total,
            "failed_calls": failed,
            "success_rate": round((total - failed) / total, 4) if total else 1,
            "avg_latency_ms": round(avg_value, 2),
            "tool_counts": tool_counts,
            "source": "database",
        }

    async def seed_if_empty(self, session: AsyncSession) -> None:
        existing = await session.scalar(select(ToolAuditLogModel.id).limit(1))
        if existing:
            return
        await self.record(
            session,
            {
                "trace_id": "demo-trace-001",
                "agent_id": 1,
                "tool_name": "knowledge_search",
                "input": {"kb_id": 1, "query": "报销流程是什么？", "top_k": 3},
                "output": {"chunks": [{"document": "demo-policy.md", "score": 0.91}]},
                "status": "success",
                "latency_ms": 42,
            },
        )


persistent_tool_audit_service = PersistentToolAuditService()
