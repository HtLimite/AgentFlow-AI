from fastapi import APIRouter

from app.schemas.workflow import WorkflowRunRequest
from app.services.workflow_engine import DEFAULT_WORKFLOW, workflow_engine

router = APIRouter()


@router.get("")
async def list_workflows() -> list[dict[str, object]]:
    return [
        {
            "id": 1,
            "name": "知识库问答工作流",
            "enabled": True,
            "node_count": len(DEFAULT_WORKFLOW.nodes),
            "edge_count": len(DEFAULT_WORKFLOW.edges),
        }
    ]


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: int) -> dict[str, object]:
    return {"id": workflow_id, "name": "知识库问答工作流", "definition": DEFAULT_WORKFLOW.model_dump()}


@router.post("/{workflow_id}/run")
async def run_workflow(workflow_id: int, payload: WorkflowRunRequest) -> dict[str, object]:
    return await workflow_engine.run(workflow_id=workflow_id, input_data=payload.input, definition=payload.definition)
