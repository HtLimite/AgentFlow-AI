class WorkflowEngine:
    async def run(self, workflow_id: int, input_data: dict[str, object]) -> dict[str, object]:
        node_runs = [
            {"node_id": "start_1", "node_type": "start", "status": "success", "output": input_data},
            {"node_id": "llm_1", "node_type": "llm", "status": "success", "output": {"answer": "workflow demo"}},
            {"node_id": "end_1", "node_type": "end", "status": "success", "output": {"done": True}},
        ]
        return {"workflow_id": workflow_id, "status": "success", "node_runs": node_runs}


workflow_engine = WorkflowEngine()
