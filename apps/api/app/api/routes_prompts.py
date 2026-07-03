from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.persistent_prompt_service import is_prompt_database_error, persistent_prompt_service
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
async def list_prompts(session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_prompt_service.list_items(session)
    except Exception as exc:
        if is_prompt_database_error(exc):
            return prompt_service.list_items()
        raise


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_prompt(payload: PromptCreateRequest, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_prompt_service.create(session, payload.name, payload.scenario, payload.content)
    except Exception as exc:
        if is_prompt_database_error(exc):
            return prompt_service.create(payload.name, payload.scenario, payload.content)
        raise


@router.put("/{prompt_id}")
async def update_prompt(prompt_id: int, payload: PromptUpdateRequest, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        item = await persistent_prompt_service.update(session, prompt_id, payload.content, payload.change_note)
    except Exception as exc:
        if is_prompt_database_error(exc):
            item = prompt_service.update(prompt_id, payload.content, payload.change_note)
        else:
            raise
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return item


@router.get("/{prompt_id}/versions")
async def list_prompt_versions(prompt_id: int, session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        versions = await persistent_prompt_service.versions(session, prompt_id)
    except Exception as exc:
        if is_prompt_database_error(exc):
            versions = prompt_service.versions(prompt_id)
        else:
            raise
    if versions is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return versions


@router.post("/{prompt_id}/test")
async def test_prompt(prompt_id: int, payload: PromptTestRequest, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        result = await persistent_prompt_service.render(session, prompt_id, payload.variables)
    except Exception as exc:
        if is_prompt_database_error(exc):
            result = prompt_service.render(prompt_id, payload.variables)
        else:
            raise
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    return result
