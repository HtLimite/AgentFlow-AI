from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter()


class EvalRunRequest(BaseModel):
    dataset_id: int = 1
    model: str = "demo-model"
    cases: list[str] = Field(default_factory=lambda: ["报销流程是什么？", "如何查询售后状态？"])


@router.get("/datasets")
async def list_eval_datasets() -> list[dict[str, object]]:
    return [{"id": 1, "name": "企业制度问答评测集", "case_count": 2}]


@router.post("/runs")
async def create_eval_run(payload: EvalRunRequest) -> dict[str, object]:
    case_results = [
        {"question": question, "score": 86 + index * 3, "reason": "演示评分：命中关键依据并给出可核验回答"}
        for index, question in enumerate(payload.cases)
    ]
    score = round(sum(item["score"] for item in case_results) / len(case_results), 2) if case_results else 0
    return {"id": 1, "status": "completed", "dataset_id": payload.dataset_id, "model": payload.model, "score": score, "cases": case_results}
