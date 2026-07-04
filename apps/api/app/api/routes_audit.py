import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserContext, require_permission
from app.services.persistent_tool_audit_service import persistent_tool_audit_service
from app.services.tool_audit_service import tool_audit_service

router = APIRouter()


@router.get("/tools")
async def list_tool_audit_records(
    ctx: UserContext = Depends(require_permission("audit:read")),
    session: AsyncSession = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    tool_name: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[dict[str, object]]:
    try:
        await persistent_tool_audit_service.seed_if_empty(session)
        return await persistent_tool_audit_service.list_records(
            session, limit=limit, offset=offset, tool_name=tool_name, status=status_filter, tenant_id=ctx.tenant_id
        )
    except SQLAlchemyError:
        await session.rollback()
        tool_audit_service.seed_if_empty()
        return tool_audit_service.list_records(limit=limit)


@router.get("/tools/summary")
async def get_tool_audit_summary(ctx: UserContext = Depends(require_permission("audit:read")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        await persistent_tool_audit_service.seed_if_empty(session)
        return await persistent_tool_audit_service.summary(session, tenant_id=ctx.tenant_id)
    except SQLAlchemyError:
        await session.rollback()
        tool_audit_service.seed_if_empty()
        return {**tool_audit_service.summary(), "source": "memory"}


@router.get("/tools/export")
async def export_tool_audit_records(
    ctx: UserContext = Depends(require_permission("audit:read")),
    session: AsyncSession = Depends(get_db),
    tool_name: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
) -> StreamingResponse:
    """Export the current tenant's audit records as a CSV download."""
    try:
        await persistent_tool_audit_service.seed_if_empty(session)
        records = await persistent_tool_audit_service.list_records(
            session, limit=10000, offset=0, tool_name=tool_name, status=status_filter, tenant_id=ctx.tenant_id
        )
    except SQLAlchemyError:
        await session.rollback()
        records = tool_audit_service.list_records(limit=10000)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "trace_id", "agent_id", "tool_name", "status", "latency_ms", "error_message", "tenant_id", "created_at"])
    for row in records:
        writer.writerow([
            row.get("id"),
            row.get("trace_id"),
            row.get("agent_id"),
            row.get("tool_name"),
            row.get("status"),
            row.get("latency_ms"),
            row.get("error_message"),
            row.get("tenant_id"),
            row.get("created_at"),
        ])
    buffer.seek(0)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tool-audit.csv"},
    )


@router.get("/tools/{record_id}")
async def get_tool_audit_record(record_id: int, ctx: UserContext = Depends(require_permission("audit:read")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        await persistent_tool_audit_service.seed_if_empty(session)
        item = await persistent_tool_audit_service.get_record(session, record_id)
    except SQLAlchemyError:
        await session.rollback()
        tool_audit_service.seed_if_empty()
        item = tool_audit_service.get_record(record_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit record not found")
    return item
