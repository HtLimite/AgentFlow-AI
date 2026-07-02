from fastapi import APIRouter

from app.api import (
    routes_agents,
    routes_chat,
    routes_dashboard,
    routes_evals,
    routes_knowledge,
    routes_models,
    routes_prompts,
    routes_system,
    routes_tools,
    routes_workflows,
)

api_router = APIRouter()
api_router.include_router(routes_system.router, prefix="/system", tags=["System"])
api_router.include_router(routes_dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(routes_models.router, prefix="/model-providers", tags=["Model Providers"])
api_router.include_router(routes_chat.router, prefix="/chat", tags=["Chat"])
api_router.include_router(routes_knowledge.router, prefix="/knowledge-bases", tags=["Knowledge Base"])
api_router.include_router(routes_agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(routes_tools.router, prefix="/tools", tags=["Tools"])
api_router.include_router(routes_workflows.router, prefix="/workflows", tags=["Workflows"])
api_router.include_router(routes_prompts.router, prefix="/prompts", tags=["Prompts"])
api_router.include_router(routes_evals.router, prefix="/evals", tags=["Evaluations"])
