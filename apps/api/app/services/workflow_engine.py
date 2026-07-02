from typing import Any

from app.schemas.workflow import WorkflowDefinition, WorkflowNode
from app.services.rag_service import rag_service


DEFAULT_WORKFLOW = WorkflowDefinition(
    nodes=[
        {"id": "start_1", "type": "start", "data": {}},
        {"id": "knowledge_1", "type": "knowledge", "data": {"kb_id": 1, "top_k": 3}},
        {"id": "llm_1", "type": "llm", "data": {"prompt": "根据知识库结果回答：{{question}}"}},
        {"id": "end_1", "type": "end", "data": {}},
    ],
    edges=[
        {"source": "start_1", "target": "knowledge_1"},
        {"source": "knowledge_1", "target": "llm_1"},
        {"source": "llm_1", "target": "end_1"},
    ],
)


class WorkflowEngine:
    async def run(self, workflow_id: int, input_data: dict[str, Any], definition: WorkflowDefinition | None = None) -> dict[str, Any]:
        workflow = definition or DEFAULT_WORKFLOW
        node_map = {node.id: node for node in workflow.nodes}
        next_map = {edge.source: edge.target for edge in workflow.edges}
        current = self._find_start(workflow)
        context: dict[str, Any] = {"input": input_data, "last": input_data}
        node_runs: list[dict[str, Any]] = []

        while current:
            node = node_map[current]
            output = await self._run_node(node, context)
            context[node.id] = output
            context["last"] = output
            node_runs.append({"node_id": node.id, "node_type": node.type, "status": "success", "input": context.get("input"), "output": output})
            if node.type == "end":
                break
            current = next_map.get(node.id)

        return {"workflow_id": workflow_id, "status": "success", "output": context.get("last"), "node_runs": node_runs}

    def _find_start(self, workflow: WorkflowDefinition) -> str:
        for node in workflow.nodes:
            if node.type == "start":
                return node.id
        raise ValueError("Workflow must contain a start node")

    async def _run_node(self, node: WorkflowNode, context: dict[str, Any]) -> dict[str, Any]:
        question = str(context.get("input", {}).get("question", ""))
        if node.type == "start":
            return dict(context.get("input", {}))
        if node.type == "knowledge":
            kb_id = int(node.data.get("kb_id", 1))
            top_k = int(node.data.get("top_k", 3))
            return await rag_service.answer(kb_id=kb_id, question=question, top_k=top_k)
        if node.type == "llm":
            last = context.get("last", {})
            return {"answer": f"工作流 LLM 节点已根据上游结果生成回答：{last.get('answer', question)}"}
        if node.type == "condition":
            return {"matched": True, "branch": "true"}
        if node.type == "http":
            return {"status_code": 200, "body": {"message": "demo"}}
        if node.type == "end":
            return dict(context.get("last", {}))
        raise ValueError(f"Unsupported node type: {node.type}")


workflow_engine = WorkflowEngine()
