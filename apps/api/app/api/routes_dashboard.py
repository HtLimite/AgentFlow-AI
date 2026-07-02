from fastapi import APIRouter

from app.services.observability_service import observability_service

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary() -> dict[str, object]:
    return observability_service.summary()


@router.get("/token-usage")
async def get_token_usage() -> list[dict[str, object]]:
    return observability_service.token_usage()


@router.get("/llm-logs")
async def get_llm_logs() -> list[dict[str, object]]:
    return observability_service.list_logs()


@router.get("/recent-errors")
async def get_recent_errors() -> list[dict[str, str]]:
    return [
        {"scenario": "embedding", "message": "provider timeout", "status": "retrying"},
        {"scenario": "chat", "message": "rate limit", "status": "degraded"},
    ]
