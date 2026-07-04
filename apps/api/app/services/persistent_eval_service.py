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
        return [{"id": item.id, "name": item.name, "description": item.description, "case_count": int(case_count or 0)} for item, case_count in result.all()]

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

    async def list_runs(self, session: AsyncSession, dataset_id: int | None = None, limit: int = 50, offset: int = 0) -> list[dict[str, object]]:
        await self._ensure_default_dataset(session)
        stmt = select(EvalRunModel).order_by(EvalRunModel.id.desc()).limit(limit).offset(offset)
        if dataset_id is not None:
            stmt = stmt.where(EvalRunModel.dataset_id == dataset_id)
        result = await session.scalars(stmt)
        return [self._serialize_run(item) for item in result.all()]

    async def get_run(self, session: AsyncSession, run_id: int) -> dict[str, object] | None:
        await self._ensure_default_dataset(session)
        item = await session.get(EvalRunModel, run_id)
        if item is None:
            return None
        return self._serialize_run(item)

    async def compare_runs(self, session: AsyncSession, run_ids: list[int]) -> dict[str, object]:
        await self._ensure_default_dataset(session)
        runs: list[dict[str, object]] = []
        for run_id in run_ids:
            item = await session.get(EvalRunModel, run_id)
            if item is not None:
                runs.append(self._serialize_run(item))
        best = min(runs, key=lambda row: float(row.get("score") or 0), default=None)
        best_id = best["id"] if best else None
        for run in runs:
            run["is_best"] = run["id"] == best_id
        return {"runs": runs, "best_run_id": best_id}

    def _serialize_run(self, item: EvalRunModel) -> dict[str, object]:
        result_json = item.result_json or {}
        # Persisted result_json may already carry id/source; ensure top-level fields are consistent.
        payload = dict(result_json)
        payload["id"] = item.id
        payload["dataset_id"] = item.dataset_id
        payload["model"] = item.model
        payload["status"] = item.status
        payload["score"] = float(item.score)
        payload["source"] = "database"
        return payload

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
        session.add_all([EvalCaseModel(dataset_id=1, question="sample question", expected_answer="sample", scoring_criteria="sample")])
        await session.commit()


persistent_eval_service = PersistentEvalService()


def is_eval_database_error(exc: Exception) -> bool:
    return isinstance(exc, SQLAlchemyError)
