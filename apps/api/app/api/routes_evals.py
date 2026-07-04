from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserContext, require_permission
from app.services.eval_service import eval_service
from app.services.persistent_eval_service import is_eval_database_error, persistent_eval_service

router = APIRouter()


class EvalRunRequest(BaseModel):
    dataset_id: int = 1
    model: str = "local-rag-evaluator"
    cases: list[str] | None = Field(default=None)


class EvalCompareRequest(BaseModel):
    run_ids: list[int] = Field(min_length=1)


@router.get("/datasets")
async def list_eval_datasets(_ctx: UserContext = Depends(require_permission("eval:read")), session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_eval_service.list_datasets(session)
    except Exception as exc:
        if is_eval_database_error(exc):
            return eval_service.list_datasets()
        raise


@router.get("/runs")
async def list_eval_runs(
    _ctx: UserContext = Depends(require_permission("eval:read")),
    session: AsyncSession = Depends(get_db),
    dataset_id: int | None = Query(default=None, description="Filter runs by dataset id"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[dict[str, object]]:
    try:
        return await persistent_eval_service.list_runs(session, dataset_id=dataset_id, limit=limit, offset=offset)
    except Exception as exc:
        if is_eval_database_error(exc):
            return eval_service.list_runs(dataset_id=dataset_id, limit=limit, offset=offset)
        raise


@router.get("/runs/{run_id}")
async def get_eval_run(run_id: int, _ctx: UserContext = Depends(require_permission("eval:read")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        item = await persistent_eval_service.get_run(session, run_id)
    except Exception as exc:
        if is_eval_database_error(exc):
            item = eval_service.get_run(run_id)
        else:
            raise
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eval run not found")
    return item


@router.post("/runs")
async def create_eval_run(payload: EvalRunRequest, _ctx: UserContext = Depends(require_permission("eval:run")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_eval_service.run(session, dataset_id=payload.dataset_id, model=payload.model, cases=payload.cases)
    except Exception as exc:
        if is_eval_database_error(exc):
            return await eval_service.run(dataset_id=payload.dataset_id, model=payload.model, cases=payload.cases)
        raise


@router.post("/runs/compare")
async def compare_eval_runs(payload: EvalCompareRequest, _ctx: UserContext = Depends(require_permission("eval:read")), session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_eval_service.compare_runs(session, payload.run_ids)
    except Exception as exc:
        if is_eval_database_error(exc):
            return eval_service.compare_runs(payload.run_ids)
        raise
