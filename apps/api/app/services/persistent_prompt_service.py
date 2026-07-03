from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import PromptTemplateModel, PromptVersionModel


class PersistentPromptService:
    async def list_items(self, session: AsyncSession) -> list[dict[str, object]]:
        await self._ensure_default_prompts(session)
        result = await session.scalars(select(PromptTemplateModel).order_by(PromptTemplateModel.id.desc()))
        return [self._serialize(item) for item in result.all()]

    async def create(self, session: AsyncSession, name: str, scenario: str, content: str) -> dict[str, object]:
        item = PromptTemplateModel(name=name, scenario=scenario, content=content, current_version=1)
        session.add(item)
        await session.flush()
        session.add(PromptVersionModel(prompt_id=item.id, version=1, content=content, change_note="initial"))
        await session.commit()
        await session.refresh(item)
        return self._serialize(item)

    async def update(self, session: AsyncSession, prompt_id: int, content: str, change_note: str = "update") -> dict[str, object] | None:
        item = await session.get(PromptTemplateModel, prompt_id)
        if item is None:
            return None
        item.current_version += 1
        item.content = content
        session.add(PromptVersionModel(prompt_id=item.id, version=item.current_version, content=content, change_note=change_note))
        await session.commit()
        await session.refresh(item)
        return self._serialize(item)

    async def versions(self, session: AsyncSession, prompt_id: int) -> list[dict[str, object]] | None:
        item = await session.get(PromptTemplateModel, prompt_id)
        if item is None:
            return None
        result = await session.scalars(
            select(PromptVersionModel).where(PromptVersionModel.prompt_id == prompt_id).order_by(PromptVersionModel.version.desc())
        )
        return [
            {"version": version.version, "content": version.content, "change_note": version.change_note, "created_at": version.created_at.isoformat() if version.created_at else None}
            for version in result.all()
        ]

    async def render(self, session: AsyncSession, prompt_id: int, variables: dict[str, str]) -> dict[str, object] | None:
        item = await session.get(PromptTemplateModel, prompt_id)
        if item is None:
            return None
        rendered = item.content
        for key, value in variables.items():
            rendered = rendered.replace("{{" + key + "}}", value)
        return {"prompt_id": prompt_id, "rendered": rendered, "variables": variables, "source": "database"}

    async def _ensure_default_prompts(self, session: AsyncSession) -> None:
        existing = await session.scalar(select(PromptTemplateModel.id).limit(1))
        if existing:
            return
        defaults = [
            ("RAG 问答模板", "rag", "请根据上下文回答：{{question}}"),
            ("Agent 工具调用模板", "agent", "你可以调用工具解决用户问题：{{question}}"),
        ]
        for name, scenario, content in defaults:
            item = PromptTemplateModel(name=name, scenario=scenario, content=content, current_version=1)
            session.add(item)
            await session.flush()
            session.add(PromptVersionModel(prompt_id=item.id, version=1, content=content, change_note="initial"))
        await session.commit()

    def _serialize(self, item: PromptTemplateModel) -> dict[str, object]:
        return {"id": item.id, "name": item.name, "scenario": item.scenario, "content": item.content, "current_version": item.current_version}


persistent_prompt_service = PersistentPromptService()


def is_prompt_database_error(exc: Exception) -> bool:
    return isinstance(exc, SQLAlchemyError)
