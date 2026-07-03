from dataclasses import dataclass
from typing import Protocol

from app.services.vector_service import vector_service


class EmbeddingProvider(Protocol):
    async def embed(self, text: str, model: str | None = None) -> list[float]:
        ...


@dataclass
class LocalEmbeddingProvider:
    dimensions: int = 64

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        return vector_service.embed(text, dimensions=self.dimensions)


class EmbeddingService:
    """Embedding facade for V2.

    Current default is deterministic local embedding for offline demos. Real providers can be
    plugged in through the same async interface without changing RAG callers.
    """

    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        self._provider = provider or LocalEmbeddingProvider()

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        return await self._provider.embed(text, model=model)

    def set_provider(self, provider: EmbeddingProvider) -> None:
        self._provider = provider


embedding_service = EmbeddingService()
