import asyncio
import json
import time
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.model_provider import get_default_model_provider_entity, get_model_provider_entity
from app.models.domain import AIModel, ModelProvider
from app.services.llm_service import LLMMessage, llm_service
from app.services.observability_service import observability_service
from app.services.persistent_observability_service import is_observability_database_error, persistent_observability_service
from app.services.provider_adapter import provider_adapter

router = APIRouter()


class ChatCompletionRequest(BaseModel):
    messages: list[LLMMessage]
    model: str | None = None
    provider_id: int | None = None
    temperature: float = 0.7
    stream: bool = False


@router.post("/completions")
async def chat_completions(payload: ChatCompletionRequest, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    provider, model_name, model_id, model_source = await _resolve_provider_and_model(session, payload)

    if provider is not None and model_name:
        try:
            result = await provider_adapter.chat(provider, payload.messages, model_name, payload.temperature)
        except Exception as exc:
            await _record_call(session, payload, provider.name, model_name, 0, 0, 0, "failed", str(exc))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail={
                    "message": "Model provider request failed",
                    "provider_id": provider.id,
                    "provider": provider.name,
                    "model": model_name,
                    "model_source": model_source,
                },
            ) from exc
        mode = "provider"
        warning = None
    else:
        result = await llm_service.complete(payload.messages, model_name, payload.temperature)
        mode = "local_fallback"
        warning = "No enabled model provider is configured. This response is local fallback output."

    await _record_call(
        session,
        payload,
        provider.name if provider else None,
        model_name or "local-fallback",
        result.usage.get("prompt_tokens", 0),
        result.usage.get("completion_tokens", 0),
        result.latency_ms,
    )
    return {
        "answer": result.content,
        "usage": result.usage,
        "latency_ms": result.latency_ms,
        "provider_id": provider.id if provider else None,
        "provider": provider.name if provider else None,
        "model": model_name,
        "model_id": model_id,
        "model_source": model_source,
        "mode": mode,
        "stream_supported": provider is not None,
        "warning": warning,
    }


async def _resolve_provider_and_model(session: AsyncSession, payload: ChatCompletionRequest) -> tuple[ModelProvider | None, str | None, int | None, str]:
    if payload.provider_id is not None:
        provider = await get_model_provider_entity(session, payload.provider_id)
        if provider is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Model provider not found")
        if not provider.enabled:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Model provider is disabled")
        if payload.model:
            model = await _find_model(session, model_name=payload.model, provider_id=provider.id)
            return provider, payload.model, model.id if model else None, "request_model"
        model = await _default_model_for_provider(session, provider.id)
        if model is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No enabled model is configured for this provider")
        return provider, model.model_name, model.id, "provider_default_model"

    if payload.model:
        model = await _find_model(session, model_name=payload.model)
        if model is not None:
            provider = await get_model_provider_entity(session, model.provider_id)
            if provider is not None and provider.enabled:
                return provider, model.model_name, model.id, "configured_model"
        provider = await get_default_model_provider_entity(session)
        if provider is not None and provider.enabled:
            return provider, payload.model, None, "request_model"
        return None, payload.model, None, "local_fallback"

    model = await _default_model(session)
    if model is not None:
        provider = await get_model_provider_entity(session, model.provider_id)
        if provider is not None and provider.enabled:
            return provider, model.model_name, model.id, "default_configured_model"

    provider = await get_default_model_provider_entity(session)
    if provider is not None and provider.enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider exists but no enabled model is configured. Add an enabled model or pass model explicitly.")
    return None, None, None, "local_fallback"


async def _find_model(session: AsyncSession, model_name: str, provider_id: int | None = None) -> AIModel | None:
    stmt = select(AIModel).where(AIModel.enabled.is_(True), AIModel.model_name == model_name)
    if provider_id is not None:
        stmt = stmt.where(AIModel.provider_id == provider_id)
    stmt = stmt.order_by(AIModel.id.desc()).limit(1)
    result = await session.scalars(stmt)
    return result.first()


async def _default_model_for_provider(session: AsyncSession, provider_id: int) -> AIModel | None:
    result = await session.scalars(select(AIModel).where(AIModel.enabled.is_(True), AIModel.provider_id == provider_id, AIModel.model_type == "chat").order_by(AIModel.id.desc()).limit(1))
    return result.first()


async def _default_model(session: AsyncSession) -> AIModel | None:
    stmt = (
        select(AIModel)
        .join(ModelProvider, AIModel.provider_id == ModelProvider.id)
        .where(AIModel.enabled.is_(True), ModelProvider.enabled.is_(True), AIModel.model_type == "chat")
        .order_by(AIModel.id.desc())
        .limit(1)
    )
    result = await session.scalars(stmt)
    return result.first()


async def _record_call(session: AsyncSession, payload: ChatCompletionRequest, provider_name: str | None, model_name: str, prompt_tokens: int, completion_tokens: int, latency_ms: int, call_status: str = "success", error_message: str | None = None) -> None:
    try:
        await persistent_observability_service.record(session, scenario="chat", model=model_name, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, latency_ms=latency_ms, provider=provider_name, status=call_status, error_message=error_message)
    except Exception as exc:
        if is_observability_database_error(exc):
            observability_service.record(scenario="chat", model=model_name, prompt_tokens=prompt_tokens, completion_tokens=completion_tokens, latency_ms=latency_ms, status=call_status)
        else:
            raise


async def _stream_answer(payload: ChatCompletionRequest, session: AsyncSession, provider: ModelProvider | None, model_name: str | None, model_source: str) -> AsyncIterator[bytes]:
    started = time.perf_counter()
    chunks: list[str] = []
    prompt_tokens = llm_service.estimate_tokens("\n".join(message.content for message in payload.messages))
    active_model = model_name or "local-fallback"
    try:
        yield f"data: {json.dumps({'type': 'meta', 'mode': 'provider' if provider else 'local_fallback', 'model': active_model, 'model_source': model_source}, ensure_ascii=False)}\n\n".encode("utf-8")
        if provider is not None and model_name:
            async for chunk in provider_adapter.stream_chat(provider, payload.messages, model_name, payload.temperature):
                chunks.append(chunk)
                yield f"data: {json.dumps({'type': 'delta', 'content': chunk}, ensure_ascii=False)}\n\n".encode("utf-8")
        else:
            result = await llm_service.complete(payload.messages, model_name, payload.temperature)
            for chunk in result.content.splitlines():
                await asyncio.sleep(0.02)
                chunks.append(chunk)
                yield f"data: {json.dumps({'type': 'delta', 'content': chunk}, ensure_ascii=False)}\n\n".encode("utf-8")
        content = "".join(chunks)
        completion_tokens = llm_service.estimate_tokens(content)
        await _record_call(
            session,
            payload,
            provider.name if provider else None,
            active_model,
            prompt_tokens,
            completion_tokens,
            int((time.perf_counter() - started) * 1000),
        )
        yield f"data: {json.dumps({'type': 'done', 'total_tokens': prompt_tokens + completion_tokens}, ensure_ascii=False)}\n\n".encode("utf-8")
    except Exception as exc:
        await _record_call(session, payload, provider.name if provider else None, active_model, prompt_tokens, 0, int((time.perf_counter() - started) * 1000), "failed", str(exc))
        yield f"data: {json.dumps({'type': 'error', 'message': str(exc)}, ensure_ascii=False)}\n\n".encode("utf-8")
    yield b"data: [DONE]\n\n"


@router.post("/completions/stream")
async def stream_chat_completions(payload: ChatCompletionRequest, session: AsyncSession = Depends(get_db)) -> StreamingResponse:
    provider, model_name, _model_id, model_source = await _resolve_provider_and_model(session, payload)
    return StreamingResponse(_stream_answer(payload, session, provider, model_name, model_source), media_type="text/event-stream")
