from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import EvalCaseModel, EvalDatasetModel, EvalRunModel
from app.services.eval_service import EvalCase, EvalDataset, eval_service


class PersistentEvalService:
    async def list_datasets(self, session: AsyncSession) -> list[dict[str, object]]:
        await self._ensure_default_dataset(session)
        result = await session.execute(
            select(EvalDatasetModel, func.count(EvalCaseModel.id).label("case_count"))
            .outerjoin(EvalCaseModel, EvalCaseModel.dataset_id == EvalDatasetModel.id)
            .group_by(EvalDatasetModel.id)
            .order_by(EvalDatasetModel.id.desc())
        )
        return [
            {"id": item.id, "name": item.name, "description": item.description, "case_count": int(case_count or 0)}
            for item, case_count in result.all()
        ]

    async def run(self, session: AsyncSession, dataset_id: int, model: str, cases: list[str] | None = None) -> dict[str, object]:
        await self._ensure_default_dataset(session)
        if cases is None:
            result = await session.scalars(select(EvalCaseModel).where(EvalCaseModel.dataset_id == dataset_id).order_by(EvalCaseModel.id.asc()))
            data = await self._run_dataset_cases(dataset_id, model, result.all())
        else:
            data = await eval_service.run(dataset_id=dataset_id, model=model, cases=cases)
        run = EvalRunModel(dataset_id=dataset_id, model=model, status="completed", score=Decimal(str(data["score"])), result_json=data)
        session.add(run)
        await session.commit()
        await session.refresh(run)
        data["id"] = run.id
        data["source"] = "database"
        return data

    async def _run_dataset_cases(self, dataset_id: int, model: str, case_models: list[EvalCaseModel]) -> dict[str, object]:
        original = eval_service._datasets.get(dataset_id)
        eval_service._datasets[dataset_id] = EvalDataset(
            id=dataset_id,
            name=original.name if original else "db eval dataset",
            description=original.description if original else "loaded from database",
            cases=[EvalCase(item.question, item.expected_answer or "", item.scoring_criteria or "") for item in case_models],
        )
        try:
            return await eval_service.run(dataset_id=dataset_id, model=model)
        finally:
            if original is None:
                eval_service._datasets.pop(dataset_id, None)
            else:
                eval_service._datasets[dataset_id] = original

    async def _ensure_default_dataset(self, session: AsyncSession) -> None:
        existing = await session.scalar(select(EvalDatasetModel.id).limit(1))
        if existing:
            return
        dataset = EvalDatasetModel(id=1, name="Default RAG eval", description="Default local eval dataset")
        session.add(dataset)
        await session.flush()
        session.add_all(
            [
                EvalCaseModel(dataset_id=1, question="What is reimbursement flow?", expected_answer="invoice approval finance payment", scoring_criteria="invoice approval finance payment"),
                EvalCaseModel(dataset_id=1, question="How to check after-sales status?", expected_answer="order ticket status", scoring_criteria="order ticket status"),
            ]
        )
        await session.commit()


persistent_eval_service = PersistentEvalService()


def is_eval_database_error(exc: Exception) -> bool:
    return isinstance(exc, SQLAlchemyError)
