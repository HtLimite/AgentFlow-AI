from fastapi import APIRouter
from pydantic import BaseModel

from app.services.agent_service import agent_service
from app.services.tool_service import tool_registry

router = APIRouter()


class AgentChatRequest(BaseModel):
    question: str
    conversation_id: int | None = None


@router.get("")
async def list_agents() -> list[dict[str, object]]:
    tools = tool_registry.list_tools()
    return [
        {
            "id": 1,
            "name": "通用工具 Agent",
            "description": "根据输入自动选择知识库检索、计算器、只读 SQL 或 HTTP 请求工具。",
            "tools": [tool["name"] for tool in tools],
            "source": "tool_registry",
        }
    ]


@router.post("/{agent_id}/chat")
async def chat_with_agent(agent_id: int, payload: AgentChatRequest) -> dict[str, object]:
    return await agent_service.chat(agent_id=agent_id, question=payload.question)
