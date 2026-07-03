from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import WorkflowDefinitionModel, WorkflowNodeRunModel, WorkflowRunModel
from app.schemas.workflow import WorkflowDefinition
from app.services.workflow_engine import DEFAULT_WORKFLOW, workflow_engine


class PersistentWorkflowService:
    async def list_workflows(self, session: AsyncSession) -> list[dict[str, object]]:
        await self._ensure_default_workflow(session)
        result = await session.scalars(select(WorkflowDefinitionModel).order_by(WorkflowDefinitionModel.id.desc()))
        return [
            {
                "id": item.id,
                "name": item.name,
                "enabled": item.enabled,
                "node_count": len(item.definition_json.get("nodes", [])),
                "edge_count": len(item.definition_json.get("edges", [])),
            }
            for item in result.all()
        ]

    async def get_workflow(self, session: AsyncSession, workflow_id: int) -> dict[str, object] | None:
        item = await session.get(WorkflowDefinitionModel, workflow_id)
        if item is None:
            return None
        return {"id": item.id, "name": item.name, "definition": item.definition_json, "enabled": item.enabled}

    async def run(self, session: AsyncSession, workflow_id: int, input_data: dict[str, object], definition: WorkflowDefinition | None = None) -> dict[str, object]:
        stored = await session.get(WorkflowDefinitionModel, workflow_id)
        effective_definition = definition
        if effective_definition is None and stored is not None:
            effective_definition = WorkflowDefinition.model_validate(stored.definition_json)
        result = await workflow_engine.run(workflow_id=workflow_id, input_data=input_data, definition=effective_definition)
        run = WorkflowRunModel(workflow_id=workflow_id, status=str(result["status"]), input_json=input_data, output_json=result.get("output"))
        session.add(run)
        await session.flush()
        for node_run in result.get("node_runs", []):
            session.add(
                WorkflowNodeRunModel(
                    run_id=run.id,
                    node_id=str(node_run.get("node_id")),
                    node_type=str(node_run.get("node_type")),
                    status=str(node_run.get("status")),
                    input_json=node_run.get("input"),
                    output_json=node_run.get("output"),
                )
            )
        await session.commit()
        result["run_id"] = run.id
        result["source"] = "database"
        return result

    async def _ensure_default_workflow(self, session: AsyncSession) -> None:
        existing = await session.scalar(select(WorkflowDefinitionModel.id).limit(1))
        if existing:
            return
        session.add(WorkflowDefinitionModel(id=1, name="知识库问答工作流", definition_json=DEFAULT_WORKFLOW.model_dump(), enabled=True))
        await session.commit()


persistent_workflow_service = PersistentWorkflowService()


def is_workflow_database_error(exc: Exception) -> bool:
    return isinstance(exc, SQLAlchemyError)
