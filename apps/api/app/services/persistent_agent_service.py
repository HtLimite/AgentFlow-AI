from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import AgentDefinitionModel
from app.services.tool_service import tool_registry


def _serialize(item: AgentDefinitionModel) -> dict[str, object]:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "system_prompt": item.system_prompt,
        "tools": item.tools or [],
        "enabled": item.enabled,
        "tenant_id": item.tenant_id,
        "source": "database",
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


class PersistentAgentService:
    async def list_agents(self, session: AsyncSession, tenant_id: int | None = None) -> list[dict[str, object]]:
        await self._ensure_default_agent(session, tenant_id)
        stmt = select(AgentDefinitionModel).order_by(AgentDefinitionModel.id.asc())
        if tenant_id is not None:
            stmt = stmt.where(AgentDefinitionModel.tenant_id == tenant_id)
        result = await session.scalars(stmt)
        return [_serialize(item) for item in result.all()]

    async def get_agent(self, session: AsyncSession, agent_id: int) -> dict[str, object] | None:
        await self._ensure_default_agent(session)
        item = await session.get(AgentDefinitionModel, agent_id)
        return _serialize(item) if item else None

    async def create_agent(self, session: AsyncSession, name: str, description: str | None, system_prompt: str | None, tools: list[str] | None, enabled: bool, tenant_id: int | None = None) -> dict[str, object]:
        item = AgentDefinitionModel(
            name=name,
            description=description,
            system_prompt=system_prompt,
            tools=tools,
            enabled=enabled,
            tenant_id=tenant_id,
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return _serialize(item)

    async def update_agent(self, session: AsyncSession, agent_id: int, name: str | None = None, description: str | None = None, system_prompt: str | None = None, tools: list[str] | None = None, enabled: bool | None = None) -> dict[str, object] | None:
        item = await session.get(AgentDefinitionModel, agent_id)
        if item is None:
            return None
        if name is not None:
            item.name = name
        if description is not None:
            item.description = description
        if system_prompt is not None:
            item.system_prompt = system_prompt
        if tools is not None:
            item.tools = tools
        if enabled is not None:
            item.enabled = enabled
        await session.commit()
        await session.refresh(item)
        return _serialize(item)

    async def delete_agent(self, session: AsyncSession, agent_id: int) -> bool:
        item = await session.get(AgentDefinitionModel, agent_id)
        if item is None:
            return False
        await session.delete(item)
        await session.commit()
        return True

    async def _ensure_default_agent(self, session: AsyncSession, tenant_id: int | None = None) -> None:
        existing = await session.scalar(select(AgentDefinitionModel.id).limit(1))
        if existing:
            return
        tool_names = [tool["name"] for tool in tool_registry.list_tools()]
        default = AgentDefinitionModel(
            id=1,
            name="通用工具 Agent",
            description="根据输入自动选择知识库检索、计算器、只读 SQL 或 HTTP 请求工具。",
            system_prompt=None,
            tools=tool_names,
            enabled=True,
            tenant_id=tenant_id,
        )
        session.add(default)
        await session.commit()


persistent_agent_service = PersistentAgentService()


def is_agent_database_error(exc: Exception) -> bool:
    return isinstance(exc, SQLAlchemyError)
