from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agent_service import agent_service

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
async def chat_with_agent(agent_id: int, payload: AgentChatRequest) -> dict[str, object]:
    return await agent_service.chat(agent_id=agent_id, question=payload.question)
