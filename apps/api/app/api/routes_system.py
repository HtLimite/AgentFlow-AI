from fastapi import APIRouter

from app.services.eval_service import eval_service
from app.services.knowledge_service import knowledge_service
from app.services.observability_service import observability_service
from app.services.tool_service import tool_registry
from app.services.workflow_engine import DEFAULT_WORKFLOW

router = APIRouter()


@router.get("/health/full")
async def full_health_check() -> dict[str, object]:
    knowledge_bases = knowledge_service.list_bases()
    tools = tool_registry.list_tools()
    datasets = eval_service.list_datasets()
    summary = observability_service.summary()
    return {
        "status": "ok",
        "modules": {
            "dashboard": True,
            "model_provider": True,
            "chat": True,
            "knowledge_base": len(knowledge_bases) > 0,
            "agent_tools": len(tools) >= 4,
            "workflow": len(DEFAULT_WORKFLOW.nodes) >= 4,
            "prompt": True,
            "eval": len(datasets) > 0,
            "observability": summary["calls_today"] >= 0,
        },
        "counts": {
            "knowledge_bases": len(knowledge_bases),
            "tools": len(tools),
            "eval_datasets": len(datasets),
            "workflow_nodes": len(DEFAULT_WORKFLOW.nodes),
        },
    }


@router.get("/verification")
async def verification_plan() -> dict[str, object]:
    return {
        "order": [
            "GET /health",
            "GET /api/system/health/full",
            "GET /api/model-providers",
            "POST /api/chat/completions",
            "GET /api/knowledge-bases",
            "POST /api/knowledge-bases/1/query",
            "GET /api/tools",
            "POST /api/agents/1/chat",
            "POST /api/workflows/1/run",
            "GET /api/prompts",
            "POST /api/evals/runs",
        ],
        "pages": [
            "/dashboard",
            "/settings",
            "/chat",
            "/knowledge",
            "/agents",
            "/workflows",
            "/prompts",
            "/evals",
            "/verification",
        ],
    }
