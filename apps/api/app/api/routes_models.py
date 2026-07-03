from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.model_provider import (
    create_ai_model,
    create_model_provider,
    delete_model_provider,
    get_model_provider,
    get_model_provider_entity,
    list_ai_models,
    list_model_providers,
    update_model_provider,
)
from app.schemas.model_provider import AIModelCreate, AIModelRead, ModelProviderCreate, ModelProviderRead, ModelProviderUpdate
from app.services.provider_adapter import provider_adapter

router = APIRouter()


@router.get("", response_model=list[ModelProviderRead])
async def list_providers(session: AsyncSession = Depends(get_db)) -> list[ModelProviderRead]:
    return await list_model_providers(session)


@router.post("", response_model=ModelProviderRead, status_code=status.HTTP_201_CREATED)
async def create_provider(payload: ModelProviderCreate, session: AsyncSession = Depends(get_db)) -> ModelProviderRead:
    return await create_model_provider(session, payload)


@router.get("/models/list", response_model=list[AIModelRead])
async def list_models(session: AsyncSession = Depends(get_db)) -> list[AIModelRead]:
    return await list_ai_models(session)


@router.post("/models", response_model=AIModelRead, status_code=status.HTTP_201_CREATED)
async def create_model(payload: AIModelCreate, session: AsyncSession = Depends(get_db)) -> AIModelRead:
    model = await create_ai_model(session, payload)
    if model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model provider not found")
    return model


@router.get("/{provider_id}", response_model=ModelProviderRead)
async def read_provider(provider_id: int, session: AsyncSession = Depends(get_db)) -> ModelProviderRead:
    provider = await get_model_provider(session, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model provider not found")
    return provider


@router.put("/{provider_id}", response_model=ModelProviderRead)
async def update_provider(provider_id: int, payload: ModelProviderUpdate, session: AsyncSession = Depends(get_db)) -> ModelProviderRead:
    provider = await update_model_provider(session, provider_id, payload)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model provider not found")
    return provider


@router.delete("/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_provider(provider_id: int, session: AsyncSession = Depends(get_db)) -> None:
    deleted = await delete_model_provider(session, provider_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model provider not found")


@router.post("/{provider_id}/test")
async def test_model_provider(provider_id: int, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    provider = await get_model_provider_entity(session, provider_id)
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model provider not found")
    if not provider.enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model provider is disabled")
    result = await provider_adapter.test(provider)
    return {
        "provider_id": provider_id,
        "ok": result.ok,
        "message": result.message,
        "latency_ms": result.latency_ms,
        "base_url": provider.base_url,
        "data": result.data,
    }
