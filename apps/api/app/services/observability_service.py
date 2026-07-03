from dataclasses import dataclass, field
from datetime import datetime, timezone
from itertools import count


@dataclass
class LLMLogRecord:
    id: int
    scenario: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    status: str
    cost: float
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ObservabilityService:
    def __init__(self) -> None:
        self._ids = count(1)
        self._logs: list[LLMLogRecord] = [
            LLMLogRecord(id=next(self._ids), scenario="chat", model="demo-model", prompt_tokens=128, completion_tokens=64, latency_ms=1800, status="success", cost=0.00032),
            LLMLogRecord(id=next(self._ids), scenario="rag", model="demo-model", prompt_tokens=256, completion_tokens=96, latency_ms=2100, status="success", cost=0.00058),
        ]

    def record(self, scenario: str, model: str, prompt_tokens: int, completion_tokens: int, latency_ms: int, status: str = "success") -> dict[str, object]:
        cost = self.estimate_cost(prompt_tokens, completion_tokens)
        item = LLMLogRecord(
            id=next(self._ids),
            scenario=scenario,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=latency_ms,
            status=status,
            cost=cost,
        )
        self._logs.append(item)
        return item.__dict__

    def estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        return round(prompt_tokens * 0.000001 + completion_tokens * 0.000002, 6)

    def list_logs(self) -> list[dict[str, object]]:
        return [item.__dict__ for item in reversed(self._logs)]

    def summary(self) -> dict[str, object]:
        total_calls = len(self._logs)
        total_tokens = sum(item.prompt_tokens + item.completion_tokens for item in self._logs)
        total_cost = round(sum(item.cost for item in self._logs), 6)
        avg_latency = round(sum(item.latency_ms for item in self._logs) / total_calls, 2) if total_calls else 0
        failed = sum(1 for item in self._logs if item.status != "success")
        return {
            "calls_today": total_calls,
            "tokens_today": total_tokens,
            "cost_today": total_cost,
            "avg_latency_ms": avg_latency,
            "failure_rate": round(failed / total_calls, 4) if total_calls else 0,
            "knowledge_bases": 1,
            "agents": 3,
            "workflow_runs": 1,
        }

    def token_usage(self) -> list[dict[str, object]]:
        return [
            {"date": "2026-07-01", "tokens": 120000, "cost": 0.18},
            {"date": "2026-07-02", "tokens": self.summary()["tokens_today"], "cost": self.summary()["cost_today"]},
        ]


observability_service = ObservabilityService()
