import re
from dataclasses import dataclass, field
from itertools import count

from app.services.rag_service import rag_service
from app.services.text_cleaner import clean_extracted_text

TERM_RE = re.compile(r"[\u4e00-\u9fff]{2,}|[a-zA-Z0-9_]{2,}")


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
        self._datasets: dict[int, EvalDataset] = {
            1: EvalDataset(
                id=1,
                name="Default RAG eval",
                description="Scores runtime RAG output against expected terms and citations.",
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
        return {"id": next(self._run_ids), "status": "completed", "dataset_id": dataset_id, "model": model, "score": score, "cases": results, "source": "runtime_rag"}

    async def _score_case(self, item: EvalCase) -> dict[str, object]:
        rag = await rag_service.answer(kb_id=1, question=item.question, top_k=3)
        answer = clean_extracted_text(str(rag.get("answer", "")))
        citations = rag.get("citations", [])
        terms = self._terms(item.expected_answer + " " + item.scoring_criteria)
        if terms:
            hits = sum(1 for term in terms if term.lower() in answer.lower())
            score = round((hits / len(terms)) * 100, 2)
            reason = f"matched_terms={hits}/{len(terms)}"
        else:
            score = 100.0 if answer else 0.0
            reason = "custom_case_without_expected_answer"
        if not citations:
            score = min(score, 60.0)
            reason += "; no_citations_cap=60"
        return {"question": item.question, "answer": answer, "score": score, "reason": reason, "citation_count": len(citations) if isinstance(citations, list) else 0, "source": rag.get("source", "unknown")}

    def _terms(self, text: str) -> set[str]:
        return {item for item in TERM_RE.findall(clean_extracted_text(text)) if item.lower() not in {"what", "how", "the", "and"}}


eval_service = EvalService()
