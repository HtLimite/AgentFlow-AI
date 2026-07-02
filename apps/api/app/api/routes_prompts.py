from itertools import count

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

router = APIRouter()

_prompt_ids = count(3)
_prompts: dict[int, dict[str, object]] = {
    1: {"id": 1, "name": "RAG 问答模板", "scenario": "rag", "content": "请根据上下文回答：{{question}}", "current_version": 1},
    2: {"id": 2, "name": "Agent 工具调用模板", "scenario": "agent", "content": "你可以调用工具解决用户问题：{{question}}", "current_version": 1},
}


class PromptCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scenario: str = Field(default="general", max_length=100)
    content: str = Field(min_length=1)


class PromptTestRequest(BaseModel):
    variables: dict[str, str] = Field(default_factory=dict)


@router.get("")
async def list_prompts() -> list[dict[str, object]]:
    return list(_prompts.values())


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_prompt(payload: PromptCreateRequest) -> dict[str, object]:
    prompt_id = next(_prompt_ids)
    item = {"id": prompt_id, "name": payload.name, "scenario": payload.scenario, "content": payload.content, "current_version": 1}
    _prompts[prompt_id] = item
    return item


@router.get("/{prompt_id}/versions")
async def list_prompt_versions(prompt_id: int) -> list[dict[str, object]]:
    item = _prompts.get(prompt_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return [{"version": item["current_version"], "content": item["content"], "change_note": "initial"}]


@router.post("/{prompt_id}/test")
async def test_prompt(prompt_id: int, payload: PromptTestRequest) -> dict[str, object]:
    item = _prompts.get(prompt_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    rendered = str(item["content"])
    for key, value in payload.variables.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return {"prompt_id": prompt_id, "rendered": rendered, "variables": payload.variables}
