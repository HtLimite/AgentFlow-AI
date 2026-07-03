from typing import Any

from app.services.knowledge_service import knowledge_service


class KnowledgeSearchTool:
    name = "knowledge_search"
    description = "检索指定知识库并返回引用片段。"
    args_schema = {"kb_id": "integer", "query": "string", "top_k": "integer"}

    async def run(self, args: dict[str, Any]) -> dict[str, Any]:
        kb_id = int(args.get("kb_id", 1))
        query = str(args.get("query", ""))
        top_k = int(args.get("top_k", 5))
        return {"chunks": knowledge_service.search(kb_id=kb_id, question=query, top_k=top_k)}
