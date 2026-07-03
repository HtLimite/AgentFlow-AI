import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.model_provider import get_default_model_provider_entity, get_model_provider_entity
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
    provider = None
    if payload.provider_id is not None:
        provider = await get_model_provider_entity(session, payload.provider_id)
    if provider is None:
        provider = await get_default_model_provider_entity(session)

    if provider is not None:
        try:
            result = await provider_adapter.chat(provider, payload.messages, payload.model or "default", payload.temperature)
        except Exception:
            result = await llm_service.complete(payload.messages, payload.model, payload.temperature)
    else:
        result = await llm_service.complete(payload.messages, payload.model, payload.temperature)

    try:
        await persistent_observability_service.record(
            session,
            scenario="chat",
            model=payload.model or "demo-model",
            prompt_tokens=result.usage.get("prompt_tokens", 0),
            completion_tokens=result.usage.get("completion_tokens", 0),
            latency_ms=result.latency_ms,
            provider=provider.name if provider else None,
        )
    except Exception as exc:
        if is_observability_database_error(exc):
            observability_service.record(
                scenario="chat",
                model=payload.model or "demo-model",
                prompt_tokens=result.usage.get("prompt_tokens", 0),
                completion_tokens=result.usage.get("completion_tokens", 0),
                latency_ms=result.latency_ms,
            )
        else:
            raise
    return {"answer": result.content, "usage": result.usage, "latency_ms": result.latency_ms, "provider_id": provider.id if provider else None}


async def _stream_answer(payload: ChatCompletionRequest) -> AsyncIterator[bytes]:
    chunks = ["正在检索上下文...", "正在调用模型...", "这是 AgentFlow-AI 的流式回答示例。"]
    for chunk in chunks:
        await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n".encode("utf-8")
    yield b"data: [DONE]\n\n"


@router.post("/completions/stream")
async def stream_chat_completions(payload: ChatCompletionRequest) -> StreamingResponse:
    return StreamingResponse(_stream_answer(payload), media_type="text/event-stream")
