from app.services.retrieval_service import retrieval_service


class RAGService:
    async def answer(self, kb_id: int, question: str, top_k: int = 5) -> dict[str, object]:
        chunks = await retrieval_service.search(kb_id=kb_id, query=question, top_k=top_k)
        return {
            "answer": "根据命中的知识库片段，建议先核对制度原文，再输出可引用的答案。",
            "citations": chunks,
            "debug": {"kb_id": kb_id, "top_k": top_k, "strategy": "vector_topk_mock"},
        }


rag_service = RAGService()
