from dataclasses import dataclass, field
from itertools import count

from app.services.judge_service import judge_service
from app.services.rag_service import rag_service
from app.services.text_cleaner import clean_extracted_text


@dataclass
class EvalCase:
    question: str
    expected_answer: str
    scoring_criteria: str


@dataclass
class EvalDataset:
    id: int
    name: str
    description: str
    cases: list[EvalCase] = field(default_factory=list)


class EvalService:
    def __init__(self) -> None:
        self._run_ids = count(1)
        self._runs: dict[int, dict[str, object]] = {}
        self._datasets: dict[int, EvalDataset] = {
            1: EvalDataset(
                id=1,
                name="Default RAG eval",
                description="Scores runtime RAG output against expected terms, citations and judge rubric.",
                cases=[EvalCase("sample question", "sample", "sample")],
            )
        }

    def list_datasets(self) -> list[dict[str, object]]:
        return [{"id": item.id, "name": item.name, "description": item.description, "case_count": len(item.cases)} for item in self._datasets.values()]

    async def run(self, dataset_id: int, model: str, cases: list[str] | None = None) -> dict[str, object]:
        dataset = self._datasets.get(dataset_id)
        eval_cases = [EvalCase(item, "", "") for item in cases] if cases else (dataset.cases if dataset else [])
        results = [await self._score_case(item) for item in eval_cases]
        score = round(sum(float(item["score"]) for item in results) / len(results), 2) if results else 0
        run_id = next(self._run_ids)
        payload = {
            "id": run_id,
            "status": "completed",
            "dataset_id": dataset_id,
            "model": model,
            "score": score,
            "cases": results,
            "source": "runtime_rag_judge",
            "judge_mode": "heuristic_judge",
        }
        self._runs[run_id] = payload
        return payload

    def list_runs(self, dataset_id: int | None = None, limit: int = 50, offset: int = 0) -> list[dict[str, object]]:
        items = list(self._runs.values())
        if dataset_id is not None:
            items = [item for item in items if item.get("dataset_id") == dataset_id]
        items = items[::-1][offset : offset + limit]
        return items

    def get_run(self, run_id: int) -> dict[str, object] | None:
        return self._runs.get(run_id)

    def compare_runs(self, run_ids: list[int]) -> dict[str, object]:
        runs = [self._runs[rid] for rid in run_ids if rid in self._runs]
        best = min(runs, key=lambda row: float(row.get("score") or 0), default=None)
        best_id = best["id"] if best else None
        for run in runs:
            run["is_best"] = run["id"] == best_id
        return {"runs": runs, "best_run_id": best_id}

    async def _score_case(self, item: EvalCase) -> dict[str, object]:
        rag = await rag_service.answer(kb_id=1, question=item.question, top_k=3)
        answer = clean_extracted_text(str(rag.get("answer", "")))
        citations = rag.get("citations", [])
        citation_count = len(citations) if isinstance(citations, list) else 0
        judge = await judge_service.judge(
            question=item.question,
            answer=answer,
            expected_answer=item.expected_answer,
            scoring_criteria=item.scoring_criteria,
            citation_count=citation_count,
        )
        return {
            "question": item.question,
            "answer": answer,
            "score": judge.score,
            "reason": judge.reason,
            "citation_count": citation_count,
            "judge_mode": judge.mode,
            "matched_terms": judge.matched_terms,
            "total_terms": judge.total_terms,
            "source": rag.get("source", "unknown"),
        }


eval_service = EvalService()
