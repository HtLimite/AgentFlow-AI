from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.observability_service import observability_service
from app.services.persistent_observability_service import is_observability_database_error, persistent_observability_service

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    try:
        return await persistent_observability_service.summary(session)
    except Exception as exc:
        if is_observability_database_error(exc):
            return observability_service.summary()
        raise


@router.get("/token-usage")
async def get_token_usage(session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_observability_service.token_usage(session)
    except Exception as exc:
        if is_observability_database_error(exc):
            return observability_service.token_usage()
        raise


@router.get("/llm-logs")
async def get_llm_logs(session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        return await persistent_observability_service.list_logs(session)
    except Exception as exc:
        if is_observability_database_error(exc):
            return observability_service.list_logs()
        raise


@router.get("/recent-errors")
async def get_recent_errors() -> list[dict[str, str]]:
    return [
        {"scenario": "embedding", "message": "provider timeout", "status": "retrying"},
        {"scenario": "chat", "message": "rate limit", "status": "degraded"},
    ]
