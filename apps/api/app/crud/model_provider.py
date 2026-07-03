from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_secret, encrypt_secret, mask_secret
from app.models.domain import AIModel, ModelProvider
from app.schemas.model_provider import (
    AIModelCreate,
    AIModelRead,
    AIModelUpdate,
    ModelProviderCreate,
    ModelProviderRead,
    ModelProviderUpdate,
)


def _read_provider(provider: ModelProvider) -> ModelProviderRead:
    try:
        api_key_masked = mask_secret(decrypt_secret(provider.api_key_encrypted))
    except Exception:
        api_key_masked = "********"

    return ModelProviderRead(
        id=provider.id,
        name=provider.name,
        provider_type=provider.provider_type,
        base_url=provider.base_url,
        api_key_masked=api_key_masked,
        enabled=provider.enabled,
        created_at=provider.created_at,
        updated_at=provider.updated_at,
    )


def _read_model(model: AIModel) -> AIModelRead:
    return AIModelRead(
        id=model.id,
        provider_id=model.provider_id,
        model_name=model.model_name,
        model_type=model.model_type,
        context_window=model.context_window,
        input_price=model.input_price,
        output_price=model.output_price,
        enabled=model.enabled,
        created_at=model.created_at,
    )


async def list_model_providers(session: AsyncSession) -> list[ModelProviderRead]:
    result = await session.scalars(select(ModelProvider).order_by(ModelProvider.id.desc()))
    return [_read_provider(provider) for provider in result.all()]


async def get_model_provider(session: AsyncSession, provider_id: int) -> ModelProviderRead | None:
    provider = await session.get(ModelProvider, provider_id)
    return _read_provider(provider) if provider else None


async def get_model_provider_entity(session: AsyncSession, provider_id: int) -> ModelProvider | None:
    return await session.get(ModelProvider, provider_id)


async def get_default_model_provider_entity(session: AsyncSession) -> ModelProvider | None:
    result = await session.scalars(select(ModelProvider).where(ModelProvider.enabled.is_(True)).order_by(ModelProvider.id.desc()).limit(1))
    return result.first()


async def create_model_provider(session: AsyncSession, payload: ModelProviderCreate) -> ModelProviderRead:
    provider = ModelProvider(
        name=payload.name,
        provider_type=payload.provider_type,
        base_url=str(payload.base_url).rstrip("/"),
        api_key_encrypted=encrypt_secret(payload.api_key),
        enabled=payload.enabled,
    )
    session.add(provider)
    await session.commit()
    await session.refresh(provider)
    return _read_provider(provider)


async def update_model_provider(session: AsyncSession, provider_id: int, payload: ModelProviderUpdate) -> ModelProviderRead | None:
    provider = await session.get(ModelProvider, provider_id)
    if provider is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if "base_url" in update_data and update_data["base_url"] is not None:
        provider.base_url = str(update_data["base_url"]).rstrip("/")
    if "api_key" in update_data and update_data["api_key"] is not None:
        provider.api_key_encrypted = encrypt_secret(update_data["api_key"])
    if "name" in update_data and update_data["name"] is not None:
        provider.name = update_data["name"]
    if "provider_type" in update_data and update_data["provider_type"] is not None:
        provider.provider_type = update_data["provider_type"]
    if "enabled" in update_data and update_data["enabled"] is not None:
        provider.enabled = update_data["enabled"]

    await session.commit()
    await session.refresh(provider)
    return _read_provider(provider)


async def delete_model_provider(session: AsyncSession, provider_id: int) -> bool:
    provider = await session.get(ModelProvider, provider_id)
    if provider is None:
        return False
    await session.delete(provider)
    await session.commit()
    return True


async def create_ai_model(session: AsyncSession, payload: AIModelCreate) -> AIModelRead | None:
    provider = await session.get(ModelProvider, payload.provider_id)
    if provider is None:
        return None

    model = AIModel(
        provider_id=payload.provider_id,
        model_name=payload.model_name,
        model_type=payload.model_type,
        context_window=payload.context_window,
        input_price=payload.input_price,
        output_price=payload.output_price,
        enabled=payload.enabled,
    )
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return _read_model(model)


async def get_ai_model(session: AsyncSession, model_id: int) -> AIModelRead | None:
    model = await session.get(AIModel, model_id)
    return _read_model(model) if model else None


async def update_ai_model(session: AsyncSession, model_id: int, payload: AIModelUpdate) -> AIModelRead | None:
    model = await session.get(AIModel, model_id)
    if model is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    if "provider_id" in update_data and update_data["provider_id"] is not None:
        provider = await session.get(ModelProvider, update_data["provider_id"])
        if provider is None:
            return None
        model.provider_id = update_data["provider_id"]
    if "model_name" in update_data and update_data["model_name"] is not None:
        model.model_name = update_data["model_name"]
    if "model_type" in update_data and update_data["model_type"] is not None:
        model.model_type = update_data["model_type"]
    if "context_window" in update_data:
        model.context_window = update_data["context_window"]
    if "input_price" in update_data:
        model.input_price = update_data["input_price"]
    if "output_price" in update_data:
        model.output_price = update_data["output_price"]
    if "enabled" in update_data and update_data["enabled"] is not None:
        model.enabled = update_data["enabled"]

    await session.commit()
    await session.refresh(model)
    return _read_model(model)


async def delete_ai_model(session: AsyncSession, model_id: int) -> bool:
    model = await session.get(AIModel, model_id)
    if model is None:
        return False
    await session.delete(model)
    await session.commit()
    return True


async def list_ai_models(session: AsyncSession) -> list[AIModelRead]:
    result = await session.scalars(select(AIModel).order_by(AIModel.id.desc()))
    return [_read_model(model) for model in result.all()]
