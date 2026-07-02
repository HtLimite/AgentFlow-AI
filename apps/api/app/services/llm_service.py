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
        content = f"已收到问题：{user_question}\n当前使用模型：{model or settings.default_chat_model}，temperature={temperature}。"
        return LLMResult(
            content=content,
            usage={"prompt_tokens": 128, "completion_tokens": 64, "total_tokens": 192},
            latency_ms=int((time.perf_counter() - started) * 1000),
        )


llm_service = LLMService()
