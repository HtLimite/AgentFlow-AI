from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.tool_service import tool_registry

router = APIRouter()


class ToolRunRequest(BaseModel):
    args: dict[str, object] = Field(default_factory=dict)


@router.get("")
async def list_tools() -> list[dict[str, object]]:
    return tool_registry.list_tools()


@router.post("/{tool_name}/run")
async def run_tool(tool_name: str, payload: ToolRunRequest) -> dict[str, object]:
    record = await tool_registry.run(tool_name, payload.args)
    return record.__dict__
