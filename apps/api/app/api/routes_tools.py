from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserContext, require_permission
from app.services.persistent_tool_audit_service import persistent_tool_audit_service
from app.services.tool_service import tool_registry

router = APIRouter()


class ToolRunRequest(BaseModel):
    args: dict[str, object] = Field(default_factory=dict)


@router.get("")
async def list_tools(_context: UserContext = Depends(require_permission("audit:read"))) -> list[dict[str, object]]:
    return tool_registry.list_tools()


@router.post("/{tool_name}/run")
async def run_tool(
    tool_name: str,
    payload: ToolRunRequest,
    context: UserContext = Depends(require_permission("agent:run")),
    session: AsyncSession = Depends(get_db),
) -> dict[str, object]:
    record = await tool_registry.run(
        tool_name,
        payload.args,
        agent_id=context.user_id,
        trace_id=f"manual-tool-{context.tenant_id}-{context.user_id}",
    )
    payload_dict = record.__dict__
    # Persist manual tool runs to the database audit log so they show up in the
    # Audit page alongside agent-triggered calls. Falls back gracefully if the
    # database is unavailable (the in-memory record is still returned).
    try:
        persisted = await persistent_tool_audit_service.record(session, payload_dict, tenant_id=context.tenant_id)
        payload_dict["persistent_audit_id"] = persisted["id"]
    except Exception:  # noqa: BLE001 - persistence is best-effort for manual runs
        await session.rollback()
        payload_dict["persistent_audit_id"] = None
    return payload_dict
