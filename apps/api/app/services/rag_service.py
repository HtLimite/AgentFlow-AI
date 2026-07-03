from app.core.database import AsyncSessionLocal
from app.services.knowledge_service import knowledge_service
from app.services.persistent_knowledge_service import is_database_error, persistent_knowledge_service


class RAGService:
    async def answer(self, kb_id: int, question: str, top_k: int = 5) -> dict[str, object]:
        try:
            async with AsyncSessionLocal() as session:
                result = await persistent_knowledge_service.answer(session, kb_id=kb_id, question=question, top_k=top_k)
            result["source"] = "database"
            return result
        except Exception as exc:
            if not is_database_error(exc):
                raise
            result = knowledge_service.answer(kb_id=kb_id, question=question, top_k=top_k)
            result["source"] = "memory_fallback"
            result["warning"] = "database unavailable; using in-memory fallback"
            return result


rag_service = RAGService()
