from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import EvalCaseModel, EvalDatasetModel, EvalRunModel
from app.services.eval_service import eval_service


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
        if cases is None:
            result = await session.scalars(select(EvalCaseModel).where(EvalCaseModel.dataset_id == dataset_id).order_by(EvalCaseModel.id.asc()))
            cases = [item.question for item in result.all()]
        data = eval_service.run(dataset_id=dataset_id, model=model, cases=cases)
        run = EvalRunModel(
            dataset_id=dataset_id,
            model=model,
            status="completed",
            score=Decimal(str(data["score"])),
            result_json=data,
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)
        data["id"] = run.id
        data["source"] = "database"
        return data

    async def _ensure_default_dataset(self, session: AsyncSession) -> None:
        existing = await session.scalar(select(EvalDatasetModel.id).limit(1))
        if existing:
            return
        dataset = EvalDatasetModel(id=1, name="企业制度问答评测集", description="用于验证 RAG 回答是否命中制度依据。")
        session.add(dataset)
        await session.flush()
        session.add_all(
            [
                EvalCaseModel(dataset_id=1, question="报销流程是什么？", expected_answer="提交发票和报销单，负责人审批，财务复核付款。", scoring_criteria="是否包含提交、审批、财务复核"),
                EvalCaseModel(dataset_id=1, question="如何查询售后状态？", expected_answer="通过订单或工单信息查询售后状态。", scoring_criteria="是否说明订单或工单维度"),
            ]
        )
        await session.commit()


persistent_eval_service = PersistentEvalService()


def is_eval_database_error(exc: Exception) -> bool:
    return isinstance(exc, SQLAlchemyError)
