from fastapi import APIRouter

router = APIRouter()


@router.get("/datasets")
async def list_eval_datasets() -> list[dict[str, object]]:
    return [{"id": 1, "name": "企业制度问答评测集", "case_count": 20}]


@router.post("/runs")
async def create_eval_run() -> dict[str, object]:
    return {"id": 1, "status": "queued", "score": None}
