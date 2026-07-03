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
        """Local fallback used only when no real provider is configured.

        It intentionally returns an explicit fallback message instead of pretending that
        a remote model was called.
        """
        started = time.perf_counter()
        user_question = next((message.content for message in reversed(messages) if message.role == "user"), "")
        content = (
            "当前没有可用的真实模型供应商，已进入本地规则回退。"
            "请在 Settings 配置 OpenAI-compatible Provider 后再次调用真实模型。\n\n"
            f"用户输入：{user_question}\n"
            f"目标模型：{model or settings.default_chat_model}，temperature={temperature}。"
        )
        prompt_tokens = self._estimate_tokens("\n".join(message.content for message in messages))
        completion_tokens = self._estimate_tokens(content)
        return LLMResult(
            content=content,
            usage={"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": prompt_tokens + completion_tokens},
            latency_ms=int((time.perf_counter() - started) * 1000),
        )

    def _estimate_tokens(self, text: str) -> int:
        return max(1, len(text) // 4)


llm_service = LLMService()
