from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserContext, require_permission
from app.services.agent_service import agent_service
from app.services.persistent_agent_service import is_agent_database_error, persistent_agent_service
from app.services.persistent_tool_audit_service import persistent_tool_audit_service
from app.services.tool_service import tool_registry

router = APIRouter()


class AgentChatRequest(BaseModel):
    question: str
    conversation_id: int | None = None


class AgentCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None
    system_prompt: str | None = None
    tools: list[str] | None = None
    enabled: bool = True


class AgentUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    system_prompt: str | None = None
    tools: list[str] | None = None
    enabled: bool | None = None


def _fallback_agent() -> dict[str, object]:
    tools = tool_registry.list_tools()
    return [
        {
            "id": 1,
            "name": "通用工具 Agent",
            "description": "根据输入自动选择知识库检索、计算器、只读 SQL 或 HTTP 请求工具。",
            "system_prompt": None,
            "tools": [tool["name"] for tool in tools],
            "enabled": True,
            "source": "runtime",
        }
    ]


@router.get("")
async def list_agents(_ctx: UserContext = Depends(require_permission("agent:run")), session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_agent_service.list_agents(session, tenant_id=_ctx.tenant_id)
    except Exception as exc:
        if is_agent_database_error(exc):
            return _fallback_agent()
        raise


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_agent(payload: AgentCreateRequest, ctx: UserContext = Depends(require_permission("agent:manage")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_agent_service.create_agent(
            session,
            name=payload.name,
            description=payload.description,
            system_prompt=payload.system_prompt,
            tools=payload.tools,
            enabled=payload.enabled,
            tenant_id=ctx.tenant_id,
        )
    except Exception as exc:
        if is_agent_database_error(exc):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Agent persistence unavailable; database required to create agents") from exc
        raise


@router.get("/{agent_id}")
async def get_agent(agent_id: int, _ctx: UserContext = Depends(require_permission("agent:run")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        item = await persistent_agent_service.get_agent(session, agent_id)
    except Exception as exc:
        if is_agent_database_error(exc):
            item = next((agent for agent in _fallback_agent() if agent["id"] == agent_id), None)
        else:
            raise
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return item


@router.put("/{agent_id}")
async def update_agent(agent_id: int, payload: AgentUpdateRequest, _ctx: UserContext = Depends(require_permission("agent:manage")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        item = await persistent_agent_service.update_agent(
            session,
            agent_id,
            name=payload.name,
            description=payload.description,
            system_prompt=payload.system_prompt,
            tools=payload.tools,
            enabled=payload.enabled,
        )
    except Exception as exc:
        if is_agent_database_error(exc):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Agent persistence unavailable; database required to update agents") from exc
        raise
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    return item


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: int, _ctx: UserContext = Depends(require_permission("agent:manage")), session: AsyncSession = Depends(get_db)) -> None:
    try:
        deleted = await persistent_agent_service.delete_agent(session, agent_id)
    except Exception as exc:
        if is_agent_database_error(exc):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Agent persistence unavailable; database required to delete agents") from exc
        raise
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")


@router.post("/{agent_id}/chat")
async def chat_with_agent(
    agent_id: int,
    payload: AgentChatRequest,
    session: AsyncSession = Depends(get_db),
    context: UserContext = Depends(require_permission("agent:run")),
) -> dict[str, object]:
    result = await agent_service.chat(agent_id=agent_id, question=payload.question)
    for call in result.get("tool_calls", []):
        if not isinstance(call, dict):
            continue
        call["agent_id"] = agent_id
        try:
            persisted = await persistent_tool_audit_service.record(session, call, tenant_id=context.tenant_id)
            call["persistent_audit_id"] = persisted["id"]
        except Exception:  # noqa: BLE001 - audit persistence is best-effort
            await session.rollback()
            call["persistent_audit_id"] = None
    result["tenant_id"] = context.tenant_id
    return result
