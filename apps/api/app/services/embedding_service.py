import math
from dataclasses import dataclass
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import AIModel, ModelProvider
from app.services.provider_adapter import provider_adapter
from app.services.vector_service import vector_service

EMBEDDING_DIMENSIONS = 1536


class EmbeddingProvider(Protocol):
    async def embed(self, text: str, model: str | None = None) -> list[float]:
        ...


@dataclass
class EmbeddingResult:
    vector: list[float]
    source: str
    model: str
    provider: str | None = None
    provider_id: int | None = None
    error: str | None = None


@dataclass
class LocalEmbeddingProvider:
    dimensions: int = EMBEDDING_DIMENSIONS

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        return vector_service.embed(text, dimensions=self.dimensions)


class EmbeddingService:
    """Embedding facade with provider-first path and deterministic local fallback."""

    def __init__(self, provider: EmbeddingProvider | None = None) -> None:
        self._provider = provider or LocalEmbeddingProvider()

    async def embed(self, text: str, model: str | None = None) -> list[float]:
        return self.normalize(await self._provider.embed(text, model=model))

    async def embed_for_rag(self, session: AsyncSession, text: str) -> EmbeddingResult:
        configured = await self._find_embedding_model(session)
        if configured is not None:
            model, provider = configured
            try:
                result = await provider_adapter.embeddings(provider, text, model.model_name)
                return EmbeddingResult(
                    vector=self.normalize(result.embedding),
                    source="provider",
                    model=model.model_name,
                    provider=provider.name,
                    provider_id=provider.id,
                )
            except Exception as exc:
                local_vector = await self.embed(text)
                return EmbeddingResult(vector=local_vector, source="local_fallback", model="local-hash-embedding", error=str(exc))
        return EmbeddingResult(vector=await self.embed(text), source="local_fallback", model="local-hash-embedding")

    async def _find_embedding_model(self, session: AsyncSession) -> tuple[AIModel, ModelProvider] | None:
        stmt = (
            select(AIModel, ModelProvider)
            .join(ModelProvider, AIModel.provider_id == ModelProvider.id)
            .where(AIModel.enabled.is_(True), ModelProvider.enabled.is_(True), AIModel.model_type == "embedding")
            .order_by(AIModel.id.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        row = result.first()
        if row is None:
            return None
        model, provider = row
        return model, provider

    def normalize(self, vector: list[float], dimensions: int = EMBEDDING_DIMENSIONS) -> list[float]:
        values = [float(item) for item in vector[:dimensions]]
        if len(values) < dimensions:
            values.extend([0.0] * (dimensions - len(values)))
        norm = math.sqrt(sum(item * item for item in values)) or 1.0
        return [round(item / norm, 6) for item in values]

    def set_provider(self, provider: EmbeddingProvider) -> None:
        self._provider = provider


embedding_service = EmbeddingService()
