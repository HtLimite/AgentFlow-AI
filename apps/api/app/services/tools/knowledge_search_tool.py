from typing import Any

from app.core.database import AsyncSessionLocal
from app.services.knowledge_service import knowledge_service
from app.services.persistent_knowledge_service import is_database_error, persistent_knowledge_service


class KnowledgeSearchTool:
    name = "knowledge_search"
    description = "检索指定知识库并返回数据库中的真实引用片段。"
    args_schema = {"kb_id": "integer", "query": "string", "top_k": "integer"}

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        kb_id = int(args.get("kb_id", 1))
        query = str(args.get("query", ""))
        top_k = int(args.get("top_k", 5))

        try:
            async with AsyncSessionLocal() as session:
                chunks = await persistent_knowledge_service.search(session, kb_id=kb_id, question=query, top_k=top_k)
            return {"chunks": chunks, "source": "database"}
        except Exception as exc:
            if not is_database_error(exc):
                raise
            return {
                "chunks": knowledge_service.search(kb_id=kb_id, question=query, top_k=top_k),
                "source": "memory_fallback",
                "warning": "database unavailable; using in-memory fallback",
            }
