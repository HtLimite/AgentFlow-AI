from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserContext, require_permission
from app.schemas.workflow import WorkflowDefinition, WorkflowRunRequest
from app.services.persistent_workflow_service import is_workflow_database_error, persistent_workflow_service
from app.services.workflow_engine import DEFAULT_WORKFLOW, workflow_engine

router = APIRouter()


class WorkflowCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    definition: WorkflowDefinition
    enabled: bool = True


class WorkflowUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    definition: WorkflowDefinition | None = None
    enabled: bool | None = None


@router.get("")
async def list_workflows(_ctx: UserContext = Depends(require_permission("workflow:read")), session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
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


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(payload: WorkflowCreateRequest, _ctx: UserContext = Depends(require_permission("workflow:manage")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_workflow_service.create_workflow(session, payload.name, payload.definition, payload.enabled)
    except Exception as exc:
        if is_workflow_database_error(exc):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Workflow persistence unavailable; database required to create workflows") from exc
        raise


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: int, _ctx: UserContext = Depends(require_permission("workflow:read")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        item = await persistent_workflow_service.get_workflow(session, workflow_id)
    except Exception as exc:
        if is_workflow_database_error(exc):
            return {"id": workflow_id, "name": "知识库问答工作流", "definition": DEFAULT_WORKFLOW.model_dump()}
        raise
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return item


@router.put("/{workflow_id}")
async def update_workflow(workflow_id: int, payload: WorkflowUpdateRequest, _ctx: UserContext = Depends(require_permission("workflow:manage")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        item = await persistent_workflow_service.update_workflow(session, workflow_id, name=payload.name, definition=payload.definition, enabled=payload.enabled)
    except Exception as exc:
        if is_workflow_database_error(exc):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Workflow persistence unavailable; database required to update workflows") from exc
        raise
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return item


@router.delete("/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workflow(workflow_id: int, _ctx: UserContext = Depends(require_permission("workflow:manage")), session: AsyncSession = Depends(get_db)) -> None:
    try:
        deleted = await persistent_workflow_service.delete_workflow(session, workflow_id)
    except Exception as exc:
        if is_workflow_database_error(exc):
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Workflow persistence unavailable; database required to delete workflows") from exc
        raise
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")


@router.post("/{workflow_id}/run")
async def run_workflow(workflow_id: int, payload: WorkflowRunRequest, _ctx: UserContext = Depends(require_permission("agent:run")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_workflow_service.run(session, workflow_id=workflow_id, input_data=payload.input, definition=payload.definition)
    except Exception as exc:
        if is_workflow_database_error(exc):
            return await workflow_engine.run(workflow_id=workflow_id, input_data=payload.input, definition=payload.definition)
        raise
