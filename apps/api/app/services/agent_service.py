from app.services.rag_service import rag_service


class AgentService:
    async def chat(self, agent_id: int, question: str) -> dict[str, object]:
        rag_result = await rag_service.answer(kb_id=1, question=question, top_k=3)
        return {
            "agent_id": agent_id,
            "answer": "Agent 已调用 knowledge_search 工具，并基于引用片段生成最终回答。",
            "tool_calls": [
                {
                    "tool_name": "knowledge_search",
                    "input": {"kb_id": 1, "query": question, "top_k": 3},
                    "output": rag_result["citations"],
                    "status": "success",
                }
            ],
        }


agent_service = AgentService()
