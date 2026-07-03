from typing import Any

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.domain import KnowledgeBase
from app.services.knowledge_service import knowledge_service
from app.services.persistent_knowledge_service import is_database_error, persistent_knowledge_service


class KnowledgeSearchTool:
    name = "knowledge_search"
    description = "检索指定知识库并返回数据库中的真实引用片段。"
    args_schema = {"kb_id": "integer optional", "query": "string", "top_k": "integer"}

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        query = str(args.get("query", ""))
        top_k = int(args.get("top_k", 5))

        try:
            async with AsyncSessionLocal() as session:
                kb_id = await self._resolve_kb_id(session, args.get("kb_id"))
                if kb_id is None:
                    return {"chunks": [], "source": "database", "warning": "No knowledge base is available"}
                chunks = await persistent_knowledge_service.search(session, kb_id=kb_id, question=query, top_k=top_k)
            return {"kb_id": kb_id, "chunks": chunks, "source": "database"}
        except Exception as exc:
            if not is_database_error(exc):
                raise
            fallback_kb_id = int(args.get("kb_id") or 1)
            return {
                "kb_id": fallback_kb_id,
                "chunks": knowledge_service.search(kb_id=fallback_kb_id, question=query, top_k=top_k),
                "source": "memory_fallback",
                "warning": "database unavailable; using in-memory fallback",
            }

    async def _resolve_kb_id(self, session, raw_kb_id: object) -> int | None:
        if raw_kb_id is not None and str(raw_kb_id).strip() != "":
            return int(raw_kb_id)
        result = await session.scalars(select(KnowledgeBase.id).order_by(KnowledgeBase.id.asc()).limit(1))
        return result.first()
