from app.services.knowledge_service import knowledge_service


class RAGService:
    async def answer(self, kb_id: int, question: str, top_k: int = 5) -> dict[str, object]:
        return knowledge_service.answer(kb_id=kb_id, question=question, top_k=top_k)


rag_service = RAGService()
