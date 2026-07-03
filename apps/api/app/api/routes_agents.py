from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserContext, get_current_context
from app.services.agent_service import agent_service
from app.services.persistent_tool_audit_service import persistent_tool_audit_service

router = APIRouter()


class AgentChatRequest(BaseModel):
    question: str
    conversation_id: int | None = None


@router.get("")
async def list_agents() -> list[dict[str, object]]:
    return [
        {"id": 1, "name": "企业制度问答 Agent", "tools": ["knowledge_search"]},
        {"id": 2, "name": "售后数据分析 Agent", "tools": ["sql_query", "calculator"]},
    ]


@router.post("/{agent_id}/chat")
async def chat_with_agent(
    agent_id: int,
    payload: AgentChatRequest,
    session: AsyncSession = Depends(get_db),
    context: UserContext = Depends(get_current_context),
) -> dict[str, object]:
    result = await agent_service.chat(agent_id=agent_id, question=payload.question)
    for call in result.get("tool_calls", []):
        if not isinstance(call, dict):
            continue
        call["agent_id"] = agent_id
        try:
            persisted = await persistent_tool_audit_service.record(session, call, tenant_id=context.tenant_id)
            call["persistent_audit_id"] = persisted["id"]
        except SQLAlchemyError:
            await session.rollback()
            call["persistent_audit_id"] = None
    result["tenant_id"] = context.tenant_id
    return result
