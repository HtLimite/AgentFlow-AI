from fastapi import APIRouter

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary() -> dict[str, object]:
    return {
        "calls_today": 1284,
        "tokens_today": 2_400_000,
        "avg_latency_ms": 1800,
        "failure_rate": 0.007,
        "knowledge_bases": 3,
        "agents": 3,
        "workflow_runs": 28,
    }


@router.get("/recent-errors")
async def get_recent_errors() -> list[dict[str, str]]:
    return [
        {"scenario": "embedding", "message": "provider timeout", "status": "retrying"},
        {"scenario": "chat", "message": "rate limit", "status": "degraded"},
    ]
