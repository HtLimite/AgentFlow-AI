from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.workflow import WorkflowRunRequest
from app.services.persistent_workflow_service import is_workflow_database_error, persistent_workflow_service
from app.services.workflow_engine import DEFAULT_WORKFLOW, workflow_engine

router = APIRouter()


@router.get("")
async def list_workflows(session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_workflow_service.list_workflows(session)
    except Exception as exc:
        if is_workflow_database_error(exc):
            return [
                {
                    "id": 1,
                    "name": "知识库问答工作流",
                    "enabled": True,
                    "node_count": len(DEFAULT_WORKFLOW.nodes),
                    "edge_count": len(DEFAULT_WORKFLOW.edges),
                }
            ]
        raise


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: int, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        item = await persistent_workflow_service.get_workflow(session, workflow_id)
    except Exception as exc:
        if is_workflow_database_error(exc):
            return {"id": workflow_id, "name": "知识库问答工作流", "definition": DEFAULT_WORKFLOW.model_dump()}
        raise
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return item


@router.post("/{workflow_id}/run")
async def run_workflow(workflow_id: int, payload: WorkflowRunRequest, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_workflow_service.run(session, workflow_id=workflow_id, input_data=payload.input, definition=payload.definition)
    except Exception as exc:
        if is_workflow_database_error(exc):
            return await workflow_engine.run(workflow_id=workflow_id, input_data=payload.input, definition=payload.definition)
        raise
