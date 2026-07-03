from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.domain import KnowledgeBase
from app.services.knowledge_service import knowledge_service
from app.services.persistent_knowledge_service import is_database_error, persistent_knowledge_service


class RAGService:
    async def answer(self, kb_id: int | None, question: str, top_k: int = 5) -> dict[str, object]:
        try:
            async with AsyncSessionLocal() as session:
                resolved_kb_id = await self._resolve_kb_id(session, kb_id)
                if resolved_kb_id is None:
                    return {"answer": "No knowledge base is available. Please create one and upload documents first.", "citations": [], "source": "database"}
                result = await persistent_knowledge_service.answer(session, kb_id=resolved_kb_id, question=question, top_k=top_k)
            result["kb_id"] = resolved_kb_id
            result["source"] = "database"
            return result
        except Exception as exc:
            if not is_database_error(exc):
                raise
            fallback_kb_id = kb_id or 1
            result = knowledge_service.answer(kb_id=fallback_kb_id, question=question, top_k=top_k)
            result["kb_id"] = fallback_kb_id
            result["source"] = "memory_fallback"
            result["warning"] = "database unavailable; using in-memory fallback"
            return result

    async def _resolve_kb_id(self, session, kb_id: int | None) -> int | None:
        if kb_id is not None:
            return kb_id
        result = await session.scalars(select(KnowledgeBase.id).order_by(KnowledgeBase.id.asc()).limit(1))
        return result.first()


rag_service = RAGService()
