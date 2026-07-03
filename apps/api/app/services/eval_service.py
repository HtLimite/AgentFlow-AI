from dataclasses import dataclass, field
from itertools import count


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
                name="企业制度问答评测集",
                description="用于验证 RAG 回答是否命中制度依据。",
                cases=[
                    EvalCase(question="报销流程是什么？", expected_answer="提交发票和报销单，负责人审批，财务复核付款。", scoring_criteria="是否包含提交、审批、财务复核"),
                    EvalCase(question="如何查询售后状态？", expected_answer="通过订单或工单信息查询售后状态。", scoring_criteria="是否说明订单或工单维度"),
                ],
            )
        }

    def list_datasets(self) -> list[dict[str, object]]:
        return [
            {"id": item.id, "name": item.name, "description": item.description, "case_count": len(item.cases)}
            for item in self._datasets.values()
        ]

    def run(self, dataset_id: int, model: str, cases: list[str] | None = None) -> dict[str, object]:
        dataset = self._datasets.get(dataset_id)
        questions = cases or [case.question for case in dataset.cases] if dataset else cases or []
        results = [self._score_case(question, index) for index, question in enumerate(questions)]
        score = round(sum(item["score"] for item in results) / len(results), 2) if results else 0
        return {
            "id": next(self._run_ids),
            "status": "completed",
            "dataset_id": dataset_id,
            "model": model,
            "score": score,
            "cases": results,
        }

    def _score_case(self, question: str, index: int) -> dict[str, object]:
        base = 86 + index * 3
        return {
            "question": question,
            "answer": f"演示回答：已根据问题“{question}”生成可核验答案。",
            "score": min(base, 95),
            "reason": "命中关键依据，结构完整，引用可追踪。",
        }


eval_service = EvalService()
