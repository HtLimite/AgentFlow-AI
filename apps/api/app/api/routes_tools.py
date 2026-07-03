from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.rbac import UserContext, require_permission
from app.services.tool_service import tool_registry

router = APIRouter()


class ToolRunRequest(BaseModel):
    args: dict[str, object] = Field(default_factory=dict)


@router.get("")
async def list_tools(_context: UserContext = Depends(require_permission("audit:read"))) -> list[dict[str, object]]:
    return tool_registry.list_tools()


@router.post("/{tool_name}/run")
async def run_tool(tool_name: str, payload: ToolRunRequest, context: UserContext = Depends(require_permission("agent:run"))) -> dict[str, object]:
    record = await tool_registry.run(tool_name, payload.args, agent_id=context.user_id, trace_id=f"manual-tool-{context.tenant_id}-{context.user_id}")
    return record.__dict__
