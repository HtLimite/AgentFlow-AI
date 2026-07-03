class RetrievalService:
    async def search(self, kb_id: int, query: str, top_k: int = 5) -> list[dict[str, object]]:
        return [
            {
                "kb_id": kb_id,
                "document": "企业制度.pdf",
                "chunk_index": 1,
                "content": f"与问题“{query}”相关的知识库片段示例。",
                "score": 0.86,
            }
        ][:top_k]


retrieval_service = RetrievalService()
