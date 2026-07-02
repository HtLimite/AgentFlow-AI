import asyncio
import json
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.llm_service import LLMMessage, llm_service

router = APIRouter()


class ChatCompletionRequest(BaseModel):
    messages: list[LLMMessage]
    model: str | None = None
    temperature: float = 0.7
    stream: bool = False


@router.post("/completions")
async def chat_completions(payload: ChatCompletionRequest) -> dict[str, object]:
    result = await llm_service.complete(payload.messages, payload.model, payload.temperature)
    return {"answer": result.content, "usage": result.usage, "latency_ms": result.latency_ms}


async def _stream_answer(payload: ChatCompletionRequest) -> AsyncIterator[bytes]:
    chunks = ["正在检索上下文...", "正在调用模型...", "这是 AgentFlow-AI 的流式回答示例。"]
    for chunk in chunks:
        await asyncio.sleep(0.1)
        yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n".encode("utf-8")
    yield b"data: [DONE]\n\n"


@router.post("/completions/stream")
async def stream_chat_completions(payload: ChatCompletionRequest) -> StreamingResponse:
    return StreamingResponse(_stream_answer(payload), media_type="text/event-stream")
