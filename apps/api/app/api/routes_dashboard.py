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
            summary = observability_service.summary()
            summary["source"] = "memory_fallback"
            return summary
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
async def get_recent_errors(session: AsyncSession = Depends(get_db)) -> list[dict[str, object]]:
    try:
        logs = await persistent_observability_service.list_logs(session, limit=50)
    except Exception as exc:
        if is_observability_database_error(exc):
            logs = observability_service.list_logs()
        else:
            raise
    return [item for item in logs if item.get("status") != "success"][:10]
