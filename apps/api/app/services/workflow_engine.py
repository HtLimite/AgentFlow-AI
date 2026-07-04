from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.workflow import WorkflowDefinition, WorkflowNode
from app.services.llm_service import LLMMessage
from app.services.provider_adapter import provider_adapter
from app.services.rag_service import rag_service


DEFAULT_WORKFLOW = WorkflowDefinition(
    nodes=[
        {"id": "start_1", "type": "start", "data": {}},
        {"id": "knowledge_1", "type": "knowledge", "data": {"top_k": 3}},
        {"id": "llm_1", "type": "llm", "data": {"prompt": "Use upstream context to answer the user question."}},
        {"id": "end_1", "type": "end", "data": {}},
    ],
    edges=[
        {"source": "start_1", "target": "knowledge_1"},
        {"source": "knowledge_1", "target": "llm_1"},
        {"source": "llm_1", "target": "end_1"},
    ],
)


class WorkflowEngine:
    async def run(self, workflow_id: int, input_data: dict[str, Any], definition: WorkflowDefinition | None = None, session: AsyncSession | None = None) -> dict[str, Any]:
        workflow = definition or DEFAULT_WORKFLOW
        node_map = {node.id: node for node in workflow.nodes}
        # Group outgoing edges by source so a node can have multiple targets
        # (e.g. a condition node branching to "true" / "false" edges).
        outgoing: dict[str, list] = {}
        for edge in workflow.edges:
            outgoing.setdefault(edge.source, []).append(edge)
        current = self._find_start(workflow)
        context: dict[str, Any] = {"input": input_data, "last": input_data}
        node_runs: list[dict[str, Any]] = []
        visited: set[str] = set()
        status = "success"

        while current:
            if current in visited:
                # Guard against cycles: stop instead of looping forever.
                node_runs.append({"node_id": current, "node_type": node_map[current].type, "status": "skipped", "input": None, "output": {"reason": "cycle detected"}})
                status = "failed"
                break
            visited.add(current)
            node = node_map[current]
            output = await self._run_node(node, context, session)
            node_status = "success" if output.get("status") not in {"failed", "skipped"} else str(output.get("status"))
            if node_status != "success":
                status = node_status
            context[node.id] = output
            context["last"] = output
            node_runs.append({"node_id": node.id, "node_type": node.type, "status": node_status, "input": context.get("input"), "output": output})
            if node.type == "end":
                break
            current = self._next_node(outgoing.get(node.id, []), node, output)

        return {"workflow_id": workflow_id, "status": status, "output": context.get("last"), "node_runs": node_runs}

    def _next_node(self, edges: list, node: WorkflowNode, output: dict[str, Any]) -> str | None:
        """Pick the next node from a node's outgoing edges.

        For condition nodes, select the edge whose ``condition`` matches the
        computed ``branch`` ("true"/"false"). For all other nodes, follow the
        first edge (falling back to any edge without a condition).
        """
        if not edges:
            return None
        if node.type == "condition":
            branch = str(output.get("branch", "false"))
            for edge in edges:
                if getattr(edge, "condition", None) is not None and str(edge.condition) == branch:
                    return edge.target
            # No condition-labelled edge matched; fall through to the first edge.
            return edges[0].target
        # Non-condition nodes: prefer an edge without a condition, else the first.
        for edge in edges:
            if getattr(edge, "condition", None) is None:
                return edge.target
        return edges[0].target

    def _find_start(self, workflow: WorkflowDefinition) -> str:
        for node in workflow.nodes:
            if node.type == "start":
                return node.id
        raise ValueError("Workflow must contain a start node")

    async def _run_node(self, node: WorkflowNode, context: dict[str, Any], session: AsyncSession | None = None) -> dict[str, Any]:
        question = str(context.get("input", {}).get("question", ""))
        if node.type == "start":
            return dict(context.get("input", {}))
        if node.type == "knowledge":
            raw_kb_id = node.data.get("kb_id")
            kb_id = int(raw_kb_id) if raw_kb_id not in {None, ""} else None
            top_k = int(node.data.get("top_k", 3))
            return await rag_service.answer(kb_id=kb_id, question=question, top_k=top_k)
        if node.type == "llm":
            return await self._run_llm_node(node, context, question, session)
        if node.type == "condition":
            key = str(node.data.get("key", ""))
            operator = str(node.data.get("operator", "equals"))
            expected = node.data.get("value", node.data.get("equals"))
            actual = context.get("input", {}).get(key) if key else context.get("last")
            if isinstance(actual, dict):
                actual = actual.get(key) if key else actual.get("answer")
            matched = self._evaluate_condition(actual, operator, expected)
            return {"matched": matched, "branch": "true" if matched else "false", "actual": actual, "expected": expected, "operator": operator}
        if node.type == "http":
            url = str(node.data.get("url", "")).strip()
            method = str(node.data.get("method", "GET")).upper()
            if not url:
                return {"status": "skipped", "reason": "HTTP node url is empty"}
            async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                response = await client.request(method, url)
            return {"status_code": response.status_code, "ok": response.is_success, "body": response.text[:2000], "source": "http"}
        if node.type == "end":
            return dict(context.get("last", {}))
        raise ValueError(f"Unsupported node type: {node.type}")

    def _evaluate_condition(self, actual: Any, operator: str, expected: Any) -> bool:
        try:
            if operator == "equals":
                return actual == expected
            if operator == "not_equals":
                return actual != expected
            if operator == "contains":
                return str(expected) in str(actual)
            if operator == "gt":
                return float(actual) > float(expected)
            if operator == "lt":
                return float(actual) < float(expected)
            if operator == "gte":
                return float(actual) >= float(expected)
            if operator == "lte":
                return float(actual) <= float(expected)
        except (TypeError, ValueError):
            return False
        # Unknown operator falls back to truthiness.
        return bool(actual)

    async def _run_llm_node(self, node: WorkflowNode, context: dict[str, Any], question: str, session: AsyncSession | None) -> dict[str, Any]:
        """Bind the LLM node to a real provider when one is configured.

        Resolves the default chat provider+model (or the node's ``model``/
        ``provider_id`` override) and calls it. Falls back to passing the
        upstream answer through only when no provider is available.
        """
        prompt_template = str(node.data.get("prompt", ""))
        upstream = context.get("last", {})
        upstream_answer = str(upstream.get("answer", "")) if isinstance(upstream, dict) else str(upstream)

        provider, model_name = await self._resolve_llm_provider(session, node.data)

        if provider is not None and model_name:
            system_prompt = prompt_template or "You are a helpful assistant. Use the provided context to answer concisely."
            user_content = upstream_answer or question
            messages: list[LLMMessage] = [
                LLMMessage(role="system", content=system_prompt),
                LLMMessage(role="user", content=user_content),
            ]
            try:
                result = await provider_adapter.chat(provider, messages=messages, model=model_name, temperature=float(node.data.get("temperature", 0.7)))
                return {
                    "answer": result.content,
                    "model": model_name,
                    "provider": provider.name,
                    "source": "provider",
                    "usage": result.usage,
                    "latency_ms": result.latency_ms,
                }
            except Exception as exc:  # noqa: BLE001 - fall back to upstream on provider error
                return {
                    "answer": upstream_answer or question,
                    "source": "provider_error_fallback",
                    "model": model_name,
                    "warning": f"Provider call failed: {exc}; upstream result passed through.",
                }

        # No provider configured: pass upstream through honestly.
        if upstream_answer:
            return {"answer": upstream_answer, "source": "upstream_context", "warning": "LLM node is not bound to a provider; upstream result was passed through."}
        return {"answer": question, "source": "input", "warning": "LLM node is not bound to a provider."}

    async def _resolve_llm_provider(self, session: AsyncSession | None, data: dict[str, Any]) -> tuple[Any, str | None]:
        if session is None:
            return None, None
        try:
            from app.crud.model_provider import get_default_model_provider_entity, get_model_provider_entity
            from app.models.domain import AIModel
            from sqlalchemy import select

            model_override = data.get("model")
            provider_id = data.get("provider_id")
            if provider_id is not None:
                provider = await get_model_provider_entity(session, int(provider_id))
                if provider is not None and provider.enabled:
                    if model_override:
                        return provider, str(model_override)
                    stmt = select(AIModel).where(AIModel.enabled.is_(True), AIModel.provider_id == provider.id, AIModel.model_type == "chat").order_by(AIModel.id.desc()).limit(1)
                    result = await session.scalars(stmt)
                    model = result.first()
                    return provider, model.model_name if model else None
                return None, None

            if model_override:
                stmt = select(AIModel).where(AIModel.enabled.is_(True), AIModel.model_name == str(model_override)).order_by(AIModel.id.desc()).limit(1)
                result = await session.scalars(stmt)
                model = result.first()
                if model is not None:
                    provider = await get_model_provider_entity(session, model.provider_id)
                    if provider is not None and provider.enabled:
                        return provider, model.model_name

            provider = await get_default_model_provider_entity(session)
            if provider is not None and provider.enabled:
                stmt = select(AIModel).where(AIModel.enabled.is_(True), AIModel.provider_id == provider.id, AIModel.model_type == "chat").order_by(AIModel.id.desc()).limit(1)
                result = await session.scalars(stmt)
                model = result.first()
                if model is not None:
                    return provider, model.model_name
                return provider, str(model_override) if model_override else None
            return None, None
        except Exception:  # noqa: BLE001 - provider resolution must never crash the workflow
            return None, None


workflow_engine = WorkflowEngine()
