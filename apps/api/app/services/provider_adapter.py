import json
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

import httpx

from app.core.security import decrypt_secret
from app.models.domain import ModelProvider
from app.services.llm_service import LLMMessage, LLMResult


@dataclass
class ProviderCallResult:
    ok: bool
    message: str
    latency_ms: int
    data: dict[str, Any]


@dataclass
class EmbeddingCallResult:
    embedding: list[float]
    usage: dict[str, int]
    latency_ms: int
    model: str


class ProviderAdapter:
    """OpenAI-compatible provider adapter used by real-call paths."""

    async def chat(self, provider: ModelProvider, messages: list[LLMMessage], model: str, temperature: float = 0.7) -> LLMResult:
        started = time.perf_counter()
        credential = decrypt_secret(provider.api_key_encrypted)
        payload = {
            "model": model,
            "messages": [message.model_dump() for message in messages],
            "temperature": temperature,
            "stream": False,
        }
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{provider.base_url.rstrip('/')}/chat/completions",
                headers=self._headers(credential),
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = body.get("usage") or {}
        return LLMResult(
            content=str(message.get("content") or ""),
            usage={
                "prompt_tokens": int(usage.get("prompt_tokens") or 0),
                "completion_tokens": int(usage.get("completion_tokens") or 0),
                "total_tokens": int(usage.get("total_tokens") or 0),
            },
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    async def stream_chat(self, provider: ModelProvider, messages: list[LLMMessage], model: str, temperature: float = 0.7) -> AsyncIterator[str]:
        credential = decrypt_secret(provider.api_key_encrypted)
        payload = {
            "model": model,
            "messages": [message.model_dump() for message in messages],
            "temperature": temperature,
            "stream": True,
        }
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{provider.base_url.rstrip('/')}/chat/completions",
                headers=self._headers(credential),
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or line.startswith(":"):
                        continue
                    data = line[5:].strip() if line.startswith("data:") else line
                    if data == "[DONE]":
                        break
                    try:
                        body = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    choice = (body.get("choices") or [{}])[0]
                    delta = choice.get("delta") or choice.get("message") or {}
                    content = delta.get("content")
                    if content:
                        yield str(content)

    async def embeddings(self, provider: ModelProvider, text: str, model: str) -> EmbeddingCallResult:
        started = time.perf_counter()
        credential = decrypt_secret(provider.api_key_encrypted)
        payload = {"model": model, "input": text}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{provider.base_url.rstrip('/')}/embeddings",
                headers=self._headers(credential),
                json=payload,
            )
            response.raise_for_status()
            body = response.json()
        data = body.get("data") or []
        first = data[0] if data else {}
        usage = body.get("usage") or {}
        return EmbeddingCallResult(
            embedding=[float(item) for item in first.get("embedding", [])],
            usage={
                "prompt_tokens": int(usage.get("prompt_tokens") or 0),
                "completion_tokens": int(usage.get("completion_tokens") or 0),
                "total_tokens": int(usage.get("total_tokens") or usage.get("prompt_tokens") or 0),
            },
            latency_ms=int((time.perf_counter() - started) * 1000),
            model=model,
        )

    async def test(self, provider: ModelProvider) -> ProviderCallResult:
        started = time.perf_counter()
        credential = decrypt_secret(provider.api_key_encrypted)
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(f"{provider.base_url.rstrip('/')}/models", headers=self._headers(credential))
            latency_ms = int((time.perf_counter() - started) * 1000)
            return ProviderCallResult(
                ok=response.status_code < 500,
                message="provider reachable" if response.status_code < 500 else "provider returned server error",
                latency_ms=latency_ms,
                data={"status_code": response.status_code},
            )
        except Exception as exc:
            latency_ms = int((time.perf_counter() - started) * 1000)
            return ProviderCallResult(ok=False, message=str(exc), latency_ms=latency_ms, data={})

    def _headers(self, credential: str) -> dict[str, str]:
        scheme = "Bearer"
        return {"Authorization": f"{scheme} {credential}", "Content-Type": "application/json"}


provider_adapter = ProviderAdapter()
