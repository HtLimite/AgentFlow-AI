from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services.eval_service import eval_service

router = APIRouter()


class EvalRunRequest(BaseModel):
    dataset_id: int = 1
    model: str = "demo-model"
    cases: list[str] | None = Field(default=None)


@router.get("/datasets")
async def list_eval_datasets() -> list[dict[str, object]]:
    return eval_service.list_datasets()


@router.post("/runs")
async def create_eval_run(payload: EvalRunRequest) -> dict[str, object]:
    return eval_service.run(dataset_id=payload.dataset_id, model=payload.model, cases=payload.cases)
