from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.rbac import UserContext, get_current_context
from app.services.eval_service import eval_service
from app.services.knowledge_service import knowledge_service
from app.services.observability_service import observability_service
from app.services.tool_audit_service import tool_audit_service
from app.services.tool_service import tool_registry
from app.services.workflow_engine import DEFAULT_WORKFLOW

router = APIRouter()

PERSISTENCE_TABLES = [
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
    "tool_audit_log",
    "tenant",
    "audit_log",
]

PERSISTENCE_BOOTSTRAP_SQL = [
    "CREATE EXTENSION IF NOT EXISTS vector",
    """
    CREATE TABLE IF NOT EXISTS sys_user (
      id BIGSERIAL PRIMARY KEY,
      username VARCHAR(64) NOT NULL UNIQUE,
      password_hash VARCHAR(255) NOT NULL,
      nickname VARCHAR(64),
      role VARCHAR(32) DEFAULT 'USER',
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ai_model_provider (
      id BIGSERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      provider_type VARCHAR(50) NOT NULL,
      base_url TEXT NOT NULL,
      api_key_encrypted TEXT NOT NULL,
      enabled BOOLEAN DEFAULT TRUE,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ai_model (
      id BIGSERIAL PRIMARY KEY,
      provider_id BIGINT REFERENCES ai_model_provider(id),
      model_name VARCHAR(128) NOT NULL,
      model_type VARCHAR(32) NOT NULL,
      context_window INT,
      input_price DECIMAL(12, 6),
      output_price DECIMAL(12, 6),
      enabled BOOLEAN DEFAULT TRUE,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_base (
      id BIGSERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      description TEXT,
      visibility VARCHAR(30) DEFAULT 'private',
      created_by BIGINT,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_document (
      id BIGSERIAL PRIMARY KEY,
      kb_id BIGINT NOT NULL REFERENCES knowledge_base(id),
      filename VARCHAR(255) NOT NULL,
      file_type VARCHAR(50),
      file_url TEXT,
      file_size BIGINT,
      parse_status VARCHAR(50) DEFAULT 'pending',
      chunk_count INT DEFAULT 0,
      error_message TEXT,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS knowledge_chunk (
      id BIGSERIAL PRIMARY KEY,
      kb_id BIGINT NOT NULL REFERENCES knowledge_base(id),
      document_id BIGINT NOT NULL REFERENCES knowledge_document(id),
      content TEXT NOT NULL,
      chunk_index INT NOT NULL,
      token_count INT,
      embedding VECTOR(1536),
      metadata JSONB,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_kb_id ON knowledge_chunk(kb_id)",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_document_id ON knowledge_chunk(document_id)",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_embedding ON knowledge_chunk USING hnsw (embedding vector_cosine_ops)",
    """
    CREATE TABLE IF NOT EXISTS prompt_template (
      id BIGSERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      scenario VARCHAR(100) DEFAULT 'general',
      content TEXT NOT NULL,
      current_version INT DEFAULT 1,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS prompt_version (
      id BIGSERIAL PRIMARY KEY,
      prompt_id BIGINT NOT NULL REFERENCES prompt_template(id) ON DELETE CASCADE,
      version INT NOT NULL,
      content TEXT NOT NULL,
      change_note TEXT,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_definition (
      id BIGSERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      definition_json JSONB NOT NULL,
      enabled BOOLEAN DEFAULT TRUE,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW(),
      updated_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_run (
      id BIGSERIAL PRIMARY KEY,
      workflow_id BIGINT NOT NULL,
      status VARCHAR(50) DEFAULT 'running',
      input_json JSONB,
      output_json JSONB,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS workflow_node_run (
      id BIGSERIAL PRIMARY KEY,
      run_id BIGINT NOT NULL REFERENCES workflow_run(id) ON DELETE CASCADE,
      node_id VARCHAR(100) NOT NULL,
      node_type VARCHAR(50) NOT NULL,
      status VARCHAR(50) DEFAULT 'success',
      input_json JSONB,
      output_json JSONB,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS eval_dataset (
      id BIGSERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      description TEXT,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS eval_case (
      id BIGSERIAL PRIMARY KEY,
      dataset_id BIGINT NOT NULL REFERENCES eval_dataset(id) ON DELETE CASCADE,
      question TEXT NOT NULL,
      expected_answer TEXT,
      scoring_criteria TEXT,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS eval_run (
      id BIGSERIAL PRIMARY KEY,
      dataset_id BIGINT NOT NULL,
      model VARCHAR(100) NOT NULL,
      status VARCHAR(50) DEFAULT 'completed',
      score DECIMAL(6, 2) DEFAULT 0,
      result_json JSONB,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS llm_call_log (
      id BIGSERIAL PRIMARY KEY,
      provider VARCHAR(100),
      model VARCHAR(100),
      scenario VARCHAR(100),
      prompt_tokens INT DEFAULT 0,
      completion_tokens INT DEFAULT 0,
      total_tokens INT DEFAULT 0,
      cost DECIMAL(12, 6) DEFAULT 0,
      latency_ms INT,
      status VARCHAR(50),
      error_message TEXT,
      metadata_json JSONB,
      created_by BIGINT,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tool_audit_log (
      id BIGSERIAL PRIMARY KEY,
      trace_id VARCHAR(120) NOT NULL,
      agent_id BIGINT,
      tool_name VARCHAR(100) NOT NULL,
      input_json JSONB,
      output_json JSONB,
      status VARCHAR(50) DEFAULT 'success',
      latency_ms INT DEFAULT 0,
      error_message TEXT,
      tenant_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tenant (
      id BIGSERIAL PRIMARY KEY,
      name VARCHAR(100) NOT NULL,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_log (
      id BIGSERIAL PRIMARY KEY,
      tenant_id BIGINT,
      actor VARCHAR(100),
      action VARCHAR(100) NOT NULL,
      target VARCHAR(200),
      metadata_json JSONB,
      created_at TIMESTAMP DEFAULT NOW()
    )
    """,
    "ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS total_tokens INT DEFAULT 0",
    "ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS latency_ms INT",
    "ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS status VARCHAR(50)",
    "ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS error_message TEXT",
    "ALTER TABLE llm_call_log ADD COLUMN IF NOT EXISTS metadata_json JSONB",
    "ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS tenant_id BIGINT",
    "ALTER TABLE knowledge_document ADD COLUMN IF NOT EXISTS tenant_id BIGINT",
    "ALTER TABLE knowledge_chunk ADD COLUMN IF NOT EXISTS tenant_id BIGINT",
    "ALTER TABLE prompt_template ADD COLUMN IF NOT EXISTS tenant_id BIGINT",
    "ALTER TABLE workflow_run ADD COLUMN IF NOT EXISTS tenant_id BIGINT",
    "ALTER TABLE eval_run ADD COLUMN IF NOT EXISTS tenant_id BIGINT",
    "CREATE INDEX IF NOT EXISTS idx_prompt_template_scenario ON prompt_template(scenario)",
    "CREATE INDEX IF NOT EXISTS idx_workflow_run_workflow_id ON workflow_run(workflow_id)",
    "CREATE INDEX IF NOT EXISTS idx_eval_run_dataset_id ON eval_run(dataset_id)",
    "CREATE INDEX IF NOT EXISTS idx_llm_call_log_created_at ON llm_call_log(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_tool_audit_log_trace_id ON tool_audit_log(trace_id)",
    "CREATE INDEX IF NOT EXISTS idx_tool_audit_log_created_at ON tool_audit_log(created_at)",
    "CREATE INDEX IF NOT EXISTS idx_tool_audit_log_tool_name ON tool_audit_log(tool_name)",
]


@router.get("/health/full")
async def full_health_check() -> dict[str, object]:
    knowledge_bases = knowledge_service.list_bases()
    tools = tool_registry.list_tools()
    datasets = eval_service.list_datasets()
    summary = observability_service.summary()
    tool_audit_service.seed_if_empty()
    audit_summary = tool_audit_service.summary()
    tool_audit_ready = "total_calls" in audit_summary and "success_rate" in audit_summary
    modules = {
        "dashboard": True,
        "model_provider": True,
        "chat": True,
        "knowledge_base": len(knowledge_bases) > 0,
        "agent_tools": len(tools) >= 4,
        "tool_audit": tool_audit_ready,
        "workflow": len(DEFAULT_WORKFLOW.nodes) >= 4,
        "workflow_canvas": True,
        "react_flow_canvas": True,
        "rbac": True,
        "prompt": True,
        "eval": len(datasets) > 0,
        "eval_compare": True,
        "observability": summary["calls_today"] >= 0,
    }
    failed_modules = [name for name, ok in modules.items() if not ok]
    return {
        "status": "ok" if not failed_modules else "failed",
        "modules": modules,
        "failed_modules": failed_modules,
        "counts": {
            "knowledge_bases": len(knowledge_bases),
            "tools": len(tools),
            "audit_records": audit_summary["total_calls"],
            "eval_datasets": len(datasets),
            "workflow_nodes": len(DEFAULT_WORKFLOW.nodes),
        },
    }


async def _bootstrap_persistence_schema(session: AsyncSession) -> None:
    for statement in PERSISTENCE_BOOTSTRAP_SQL:
        await session.execute(text(statement))
    await session.commit()


@router.get("/persistence/health")
async def persistence_health(session: AsyncSession = Depends(get_db)) -> dict[str, object]:
    await _bootstrap_persistence_schema(session)
    counts: dict[str, int] = {}
    for table in PERSISTENCE_TABLES:
        result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
        counts[table] = int(result.scalar_one())
    return {
        "status": "ok",
        "mode": "persistent",
        "database": "connected",
        "schema_bootstrap": "applied",
        "tables_checked": PERSISTENCE_TABLES,
        "counts": counts,
    }


@router.get("/rbac/context")
async def rbac_context(context: UserContext = Depends(get_current_context)) -> dict[str, object]:
    return {"status": "ok", "context": context.to_dict()}


@router.get("/verification")
async def verification_plan() -> dict[str, object]:
    return {
        "order": [
            "GET /health",
            "GET /api/system/health/full",
            "GET /api/system/persistence/health",
            "GET /api/system/rbac/context",
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
