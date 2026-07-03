from fastapi import APIRouter, HTTPException, status

from app.services.tool_audit_service import tool_audit_service

router = APIRouter()


@router.get("/tools")
async def list_tool_audit_records(limit: int = 50) -> list[dict[str, object]]:
    return tool_audit_service.list_records(limit=limit)


@router.get("/tools/summary")
async def get_tool_audit_summary() -> dict[str, object]:
    return tool_audit_service.summary()


@router.get("/tools/{record_id}")
async def get_tool_audit_record(record_id: int) -> dict[str, object]:
    item = tool_audit_service.get_record(record_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Audit record not found")
    return item
