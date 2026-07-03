import time

from pydantic import BaseModel

from app.core.config import settings


class LLMMessage(BaseModel):
    role: str
    content: str


class LLMResult(BaseModel):
    content: str
    usage: dict[str, int]
    latency_ms: int


class LLMService:
    async def complete(self, messages: list[LLMMessage], model: str | None = None, temperature: float = 0.7) -> LLMResult:
        started = time.perf_counter()
        user_question = next((message.content for message in reversed(messages) if message.role == "user"), "")
        content = (
            "No real model provider is configured. This is local fallback output, not a remote LLM result.\n\n"
            f"User input: {user_question}\n"
            f"Target model: {model or settings.default_chat_model}, temperature={temperature}."
        )
        prompt_tokens = self.estimate_tokens("\n".join(message.content for message in messages))
        completion_tokens = self.estimate_tokens(content)
        return LLMResult(
            content=content,
            usage={"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": prompt_tokens + completion_tokens},
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def estimate_tokens(self, text: str) -> int:
        return self._estimate_tokens(text)

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)


llm_service = LLMService()
