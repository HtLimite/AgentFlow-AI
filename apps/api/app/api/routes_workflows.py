from fastapi import APIRouter
from pydantic import BaseModel

from app.services.workflow_engine import workflow_engine

router = APIRouter()


class WorkflowRunRequest(BaseModel):
    input: dict[str, object]


@router.get("")
async def list_workflows() -> list[dict[str, object]]:
    return [{"id": 1, "name": "知识库问答工作流", "enabled": True}]


@router.post("/{workflow_id}/run")
async def run_workflow(workflow_id: int, payload: WorkflowRunRequest) -> dict[str, object]:
    return await workflow_engine.run(workflow_id=workflow_id, input_data=payload.input)
