from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.persistent_tool_audit_service import persistent_tool_audit_service
from app.services.tool_audit_service import tool_audit_service

router = APIRouter()


@router.get("/tools")
async def list_tool_audit_records(
    limit: int = Query(default=50, ge=1, le=200),
    tool_name: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, object]]:
    try:
        await persistent_tool_audit_service.seed_if_empty(session)
        return await persistent_tool_audit_service.list_records(session, limit=limit, tool_name=tool_name, status=status_filter)
    except SQLAlchemyError:
        await session.rollback()
        tool_audit_service.seed_if_empty()
        return tool_audit_service.list_records(limit=limit)


@router.get("/tools/summary")
async def get_tool_audit_summary(session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        await persistent_tool_audit_service.seed_if_empty(session)
        return await persistent_tool_audit_service.summary(session)
    except SQLAlchemyError:
        await session.rollback()
        tool_audit_service.seed_if_empty()
        return {**tool_audit_service.summary(), "source": "memory"}


@router.get("/tools/{record_id}")
async def get_tool_audit_record(record_id: int, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
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
