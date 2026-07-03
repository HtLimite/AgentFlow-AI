from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.eval_service import eval_service
from app.services.knowledge_service import knowledge_service
from app.services.observability_service import observability_service
from app.services.tool_audit_service import tool_audit_service
from app.services.tool_service import tool_registry
from app.services.workflow_engine import DEFAULT_WORKFLOW

router = APIRouter()


@router.get("/health/full")
async def full_health_check() -> dict[str, object]:
    knowledge_bases = knowledge_service.list_bases()
    tools = tool_registry.list_tools()
    datasets = eval_service.list_datasets()
    summary = observability_service.summary()
    tool_audit_service.seed_if_empty()
    audit_summary = tool_audit_service.summary()
    return {
        "status": "ok",
        "modules": {
            "dashboard": True,
            "model_provider": True,
            "chat": True,
            "knowledge_base": len(knowledge_bases) > 0,
            "agent_tools": len(tools) >= 4,
            "tool_audit": audit_summary["total_calls"] >= 1,
            "workflow": len(DEFAULT_WORKFLOW.nodes) >= 4,
            "workflow_canvas": True,
            "prompt": True,
            "eval": len(datasets) > 0,
            "eval_compare": True,
            "observability": summary["calls_today"] >= 0,
        },
        "counts": {
            "knowledge_bases": len(knowledge_bases),
            "tools": len(tools),
            "audit_records": audit_summary["total_calls"],
            "eval_datasets": len(datasets),
            "workflow_nodes": len(DEFAULT_WORKFLOW.nodes),
        },
    }


@router.get("/persistence/health")
async def persistence_health(session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    table_names = [
        "ai_model_provider",
        "knowledge_base",
        "knowledge_document",
        "knowledge_chunk",
        "prompt_template",
        "prompt_version",
        "workflow_definition",
        "workflow_run",
        "workflow_node_run",
        "eval_dataset",
        "eval_case",
        "eval_run",
        "llm_call_log",
    ]
    counts: dict[str, int] = {}
    for table in table_names:
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
        counts[table] = int(result.scalar_one())
    return {
        "status": "ok",
        "mode": "persistent",
        "database": "connected",
        "tables_checked": table_names,
        "counts": counts,
    }


@router.get("/verification")
async def verification_plan() -> dict[str, object]:
    return {
        "order": [
            "GET /health",
            "GET /api/system/health/full",
            "GET /api/system/persistence/health",
            "GET /api/model-providers",
            "POST /api/chat/completions",
            "GET /api/knowledge-bases",
            "POST /api/knowledge-bases/1/query",
            "GET /api/tools",
            "POST /api/agents/1/chat",
            "GET /api/audit/tools/summary",
            "GET /api/audit/tools",
            "POST /api/workflows/1/run",
            "GET /api/prompts",
            "POST /api/evals/runs",
        ],
        "pages": [
            "/demo",
            "/showcase",
            "/dashboard",
            "/settings",
            "/chat",
            "/knowledge",
            "/agents",
            "/workflows",
            "/audit",
            "/prompts",
            "/evals",
            "/verification",
        ],
    }
