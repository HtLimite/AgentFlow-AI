from app.services.tool_service import tool_registry


class AgentService:
    async def chat(self, agent_id: int, question: str) -> dict[str, object]:
        tool_name = self._select_tool(question)
        args = self._build_tool_args(tool_name, question)
        tool_call = await tool_registry.run(tool_name, args)
        answer = self._build_answer(question, tool_call.output, tool_call.status)
        return {
            "agent_id": agent_id,
            "answer": answer,
            "tool_calls": [tool_call.__dict__],
        }

    def _select_tool(self, question: str) -> str:
        lowered = question.lower()
        if any(symbol in lowered for symbol in ["+", "-", "*", "/"]):
            return "calculator"
        if "sql" in lowered or "订单" in question or "售后" in question:
            return "sql_query"
        if "http" in lowered or "api" in lowered:
            return "http_request"
        return "knowledge_search"

    def _build_tool_args(self, tool_name: str, question: str) -> dict[str, object]:
        if tool_name == "calculator":
            expression = question.replace("计算", "").strip() or "1+1"
            return {"expression": expression}
        if tool_name == "sql_query":
            return {"sql": "SELECT date, orders, refunds FROM demo_after_sales LIMIT 10"}
        if tool_name == "http_request":
            return {"method": "GET", "url": "https://example.com/api/demo"}
        return {"kb_id": 1, "query": question, "top_k": 3}

    def _build_answer(self, question: str, output: dict[str, object], status: str) -> str:
        if status != "success":
            return "Agent 工具调用失败，请查看 tool_calls 中的错误信息。"
        return f"Agent 已根据问题“{question}”调用工具，并生成可追踪回答。"


agent_service = AgentService()
