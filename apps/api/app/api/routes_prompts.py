from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.prompt_service import prompt_service

router = APIRouter()


class PromptCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    scenario: str = Field(default="general", max_length=100)
    content: str = Field(min_length=1)


class PromptUpdateRequest(BaseModel):
    content: str = Field(min_length=1)
    change_note: str = "update"


class PromptTestRequest(BaseModel):
    variables: dict[str, str] = Field(default_factory=dict)


@router.get("")
async def list_prompts() -> list[dict[str, object]]:
    return prompt_service.list_items()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_prompt(payload: PromptCreateRequest) -> dict[str, object]:
    return prompt_service.create(payload.name, payload.scenario, payload.content)


@router.put("/{prompt_id}")
async def update_prompt(prompt_id: int, payload: PromptUpdateRequest) -> dict[str, object]:
    item = prompt_service.update(prompt_id, payload.content, payload.change_note)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return item


@router.get("/{prompt_id}/versions")
async def list_prompt_versions(prompt_id: int) -> list[dict[str, object]]:
    versions = prompt_service.versions(prompt_id)
    if versions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return versions


@router.post("/{prompt_id}/test")
async def test_prompt(prompt_id: int, payload: PromptTestRequest) -> dict[str, object]:
    result = prompt_service.render(prompt_id, payload.variables)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return result
