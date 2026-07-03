from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.eval_service import eval_service
from app.services.persistent_eval_service import is_eval_database_error, persistent_eval_service

router = APIRouter()


class EvalRunRequest(BaseModel):
    dataset_id: int = 1
    model: str = "demo-model"
    cases: list[str] | None = Field(default=None)


@router.get("/datasets")
async def list_eval_datasets(session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_eval_service.list_datasets(session)
    except Exception as exc:
        if is_eval_database_error(exc):
            return eval_service.list_datasets()
        raise


@router.post("/runs")
async def create_eval_run(payload: EvalRunRequest, session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_eval_service.run(session, dataset_id=payload.dataset_id, model=payload.model, cases=payload.cases)
    except Exception as exc:
        if is_eval_database_error(exc):
            return eval_service.run(dataset_id=payload.dataset_id, model=payload.model, cases=payload.cases)
        raise
