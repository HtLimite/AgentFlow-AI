import re
from typing import Any
from uuid import uuid4

from app.services.tool_service import tool_registry

URL_RE = re.compile(r"https?://[^\s，。；;]+", re.IGNORECASE)
SQL_RE = re.compile(r"\b(select|with)\b[\s\S]+", re.IGNORECASE)
EXPRESSION_RE = re.compile(r"[-+*/().\d\s]+")


class AgentService:
    async def chat(self, agent_id: int, question: str) -> dict[str, object]:
        trace_id = f"agent-{agent_id}-{uuid4().hex[:10]}"
        tool_name = self._select_tool(question)
        args = self._build_tool_args(tool_name, question)
        tool_call = await tool_registry.run(tool_name, args, agent_id=agent_id, trace_id=trace_id)
        answer = self._build_answer(question, tool_call.output, tool_call.status, tool_call.error_message)
        return {
            "agent_id": agent_id,
            "trace_id": trace_id,
            "answer": answer,
            "tool_calls": [tool_call.__dict__],
        }

    def _select_tool(self, question: str) -> str:
        lowered = question.lower()
        if URL_RE.search(question) or "http" in lowered or "api" in lowered:
            return "http_request"
        if SQL_RE.search(question):
            return "sql_query"
        if self._extract_expression(question):
            return "calculator"
        return "knowledge_search"

    def _build_tool_args(self, tool_name: str, question: str) -> dict[str, object]:
        if tool_name == "calculator":
            expression = self._extract_expression(question)
            if not expression:
                raise ValueError("未识别到可计算表达式")
            return {"expression": expression}
        if tool_name == "sql_query":
            match = SQL_RE.search(question)
            if not match:
                raise ValueError("请在问题中提供明确的 SELECT / WITH 只读 SQL")
            return {"sql": match.group(0).strip(), "max_rows": 100}
        if tool_name == "http_request":
            match = URL_RE.search(question)
            if not match:
                raise ValueError("请在问题中提供完整 http/https URL")
            return {"method": "GET", "url": match.group(0)}
        return {"kb_id": 1, "query": question, "top_k": 3}

    def _extract_expression(self, question: str) -> str | None:
        if not any(symbol in question for symbol in ["+", "-", "*", "/"]):
            return None
        candidates = [item.strip() for item in EXPRESSION_RE.findall(question)]
        candidates = [item for item in candidates if any(symbol in item for symbol in ["+", "-", "*", "/"])]
        return max(candidates, key=len) if candidates else None

    def _build_answer(self, question: str, output: dict[str, Any], status: str, error_message: str | None) -> str:
        if status != "success":
            return f"Agent 工具调用失败：{error_message or 'unknown error'}。"
        if "result" in output:
            return f"计算结果：{output['result']}。"
        if "rows" in output:
            return f"SQL 已真实执行，返回 {output.get('row_count', len(output.get('rows', [])))} 行。"
        if "status_code" in output:
            return f"HTTP 请求已真实执行，状态码 {output.get('status_code')}，ok={output.get('ok')}。"
        chunks = output.get("chunks")
        if isinstance(chunks, list):
            if not chunks:
                return f"知识库中没有找到与“{question}”直接相关的引用片段。"
            documents = sorted({str(item.get("document", "unknown")) for item in chunks if isinstance(item, dict)})
            return f"知识库检索命中 {len(chunks)} 个片段，来源：{', '.join(documents)}。"
        return "Agent 已完成工具调用，具体结果见 tool_calls。"


agent_service = AgentService()
