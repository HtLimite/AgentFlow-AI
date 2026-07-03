from dataclasses import dataclass, field
from itertools import count


@dataclass
class PromptTemplate:
    id: int
    name: str
    scenario: str
    content: str
    current_version: int = 1
    versions: list[dict[str, object]] = field(default_factory=list)


class PromptService:
    def __init__(self) -> None:
        self._ids = count(3)
        self._items: dict[int, PromptTemplate] = {
            1: PromptTemplate(id=1, name="RAG 问答模板", scenario="rag", content="请根据上下文回答：{{question}}"),
            2: PromptTemplate(id=2, name="Agent 工具调用模板", scenario="agent", content="你可以调用工具解决用户问题：{{question}}"),
        }
        for item in self._items.values():
            item.versions.append({"version": 1, "content": item.content, "change_note": "initial"})

    def list_items(self) -> list[dict[str, object]]:
        return [self._serialize(item) for item in self._items.values()]

    def create(self, name: str, scenario: str, content: str) -> dict[str, object]:
        prompt_id = next(self._ids)
        item = PromptTemplate(id=prompt_id, name=name, scenario=scenario, content=content)
        item.versions.append({"version": 1, "content": content, "change_note": "initial"})
        self._items[prompt_id] = item
        return self._serialize(item)

    def update(self, prompt_id: int, content: str, change_note: str = "update") -> dict[str, object] | None:
        item = self._items.get(prompt_id)
        if item is None:
            return None
        item.current_version += 1
        item.content = content
        item.versions.append({"version": item.current_version, "content": content, "change_note": change_note})
        return self._serialize(item)

    def versions(self, prompt_id: int) -> list[dict[str, object]] | None:
        item = self._items.get(prompt_id)
        return item.versions if item else None

    def render(self, prompt_id: int, variables: dict[str, str]) -> dict[str, object] | None:
        item = self._items.get(prompt_id)
        if item is None:
            return None
        rendered = item.content
        for key, value in variables.items():
            rendered = rendered.replace("{{" + key + "}}", value)
        return {"prompt_id": prompt_id, "rendered": rendered, "variables": variables}

    def _serialize(self, item: PromptTemplate) -> dict[str, object]:
        return {
            "id": item.id,
            "name": item.name,
            "scenario": item.scenario,
            "content": item.content,
            "current_version": item.current_version,
        }


prompt_service = PromptService()
