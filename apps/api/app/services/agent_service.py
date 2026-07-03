import re
from typing import Any
from uuid import uuid4

from app.services.tool_service import tool_registry

URL_RE = re.compile(r"https?://[^\s，。；;]+", re.IGNORECASE)
SQL_RE = re.compile(r"\bselect\b[\s\S]+", re.IGNORECASE)
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
                raise ValueError("No calculable expression found")
            return {"expression": expression}
        if tool_name == "sql_query":
            match = SQL_RE.search(question)
            if not match:
                raise ValueError("Please provide an explicit SELECT statement")
            return {"sql": match.group(0).strip(), "max_rows": 100}
        if tool_name == "http_request":
            match = URL_RE.search(question)
            if not match:
                raise ValueError("Please provide a full http/https URL")
            return {"method": "GET", "url": match.group(0)}
        return {"query": question, "top_k": 3}

    def _extract_expression(self, question: str) -> str | None:
        if not any(symbol in question for symbol in ["+", "-", "*", "/"]):
            return None
        candidates = [item.strip() for item in EXPRESSION_RE.findall(question)]
        candidates = [item for item in candidates if any(symbol in item for symbol in ["+", "-", "*", "/"])]
        return max(candidates, key=len) if candidates else None

    def _build_answer(self, question: str, output: dict[str, Any], status: str, error_message: str | None) -> str:
        if status != "success":
            return f"Tool call failed: {error_message or 'unknown error'}"
        if "result" in output:
            return f"Calculation result: {output['result']}"
        if "rows" in output:
            return f"SQL executed against database, returned {output.get('row_count', len(output.get('rows', [])))} rows."
        if "status_code" in output:
            return f"HTTP request executed, status={output.get('status_code')}, ok={output.get('ok')}."
        chunks = output.get("chunks")
        if isinstance(chunks, list):
            if not chunks:
                return f"No directly relevant citations found for: {question}"
            documents = sorted({str(item.get("document", "unknown")) for item in chunks if isinstance(item, dict)})
            return f"Knowledge search found {len(chunks)} chunks from: {', '.join(documents)}."
        return "Tool call completed. See tool_calls for details."


agent_service = AgentService()
