from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import LLMCallLog


class PersistentObservabilityService:
    async def record(
        self,
        session: AsyncSession,
        scenario: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
        latency_ms: int,
        status: str = "success",
        provider: str | None = None,
        error_message: str | None = None,
    ) -> dict[str, object]:
        cost = self.estimate_cost(prompt_tokens, completion_tokens)
        item = LLMCallLog(
            provider=provider,
            model=model,
            scenario=scenario,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            latency_ms=latency_ms,
            status=status,
            error_message=error_message,
            cost=Decimal(str(cost)),
            metadata_json={"source": "database"},
        )
        session.add(item)
        await session.commit()
        await session.refresh(item)
        return self._serialize_log(item)

    async def list_logs(self, session: AsyncSession, limit: int = 50) -> list[dict[str, object]]:
        result = await session.scalars(select(LLMCallLog).order_by(LLMCallLog.id.desc()).limit(limit))
        return [self._serialize_log(item) for item in result.all()]

    async def summary(self, session: AsyncSession) -> dict[str, object]:
        row = (
            await session.execute(
                select(
                    func.count(LLMCallLog.id),
                    func.coalesce(func.sum(LLMCallLog.prompt_tokens + LLMCallLog.completion_tokens), 0),
                    func.coalesce(func.sum(LLMCallLog.cost), 0),
                    func.coalesce(func.avg(LLMCallLog.latency_ms), 0),
                )
            )
        ).one()
        total_calls = int(row[0] or 0)
        failed = int(await session.scalar(select(func.count(LLMCallLog.id)).where(LLMCallLog.status != "success")) or 0)
        return {
            "calls_today": total_calls,
            "tokens_today": int(row[1] or 0),
            "cost_today": float(row[2] or 0),
            "avg_latency_ms": round(float(row[3] or 0), 2),
            "failure_rate": round(failed / total_calls, 4) if total_calls else 0,
            "knowledge_bases": 1,
            "agents": 3,
            "workflow_runs": 1,
            "source": "database",
        }

    async def token_usage(self, session: AsyncSession) -> list[dict[str, object]]:
        result = await session.execute(
            select(
                func.date(LLMCallLog.created_at).label("date"),
                func.coalesce(func.sum(LLMCallLog.prompt_tokens + LLMCallLog.completion_tokens), 0).label("tokens"),
                func.coalesce(func.sum(LLMCallLog.cost), 0).label("cost"),
            )
            .group_by(func.date(LLMCallLog.created_at))
            .order_by(func.date(LLMCallLog.created_at))
        )
        return [{"date": str(date), "tokens": int(tokens or 0), "cost": float(cost or 0)} for date, tokens, cost in result.all()]

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return round(prompt_tokens * 0.000001 + completion_tokens * 0.000002, 6)

    def _serialize_log(self, item: LLMCallLog) -> dict[str, object]:
        return {
            "id": item.id,
            "provider": item.provider,
            "model": item.model,
            "scenario": item.scenario,
            "prompt_tokens": item.prompt_tokens,
            "completion_tokens": item.completion_tokens,
            "total_tokens": item.total_tokens,
            "latency_ms": item.latency_ms,
            "status": item.status,
            "error_message": item.error_message,
            "cost": float(item.cost or 0),
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }


persistent_observability_service = PersistentObservabilityService()


def is_observability_database_error(exc: Exception) -> bool:
    return isinstance(exc, SQLAlchemyError)
