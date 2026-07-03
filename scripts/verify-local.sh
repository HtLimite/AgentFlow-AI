#!/usr/bin/env bash
set -euo pipefail
API="${AGENTFLOW_API_URL:-http://localhost:8000}"

echo "[1/14] Health"
curl -sS "$API/health" | cat

echo "\n[2/14] Full system health"
curl -sS "$API/api/system/health/full" | cat

echo "\n[3/14] Persistence health"
curl -sS "$API/api/system/persistence/health" | cat

echo "\n[4/14] RBAC context"
curl -sS "$API/api/system/rbac/context" -H "X-Tenant-Id: 1" -H "X-User-Role: admin" | cat

echo "\n[5/14] Dashboard summary"
curl -sS "$API/api/dashboard/summary" | cat

echo "\n[6/14] Knowledge bases"
curl -sS "$API/api/knowledge-bases" | cat

echo "\n[7/14] Knowledge query"
curl -sS -X POST "$API/api/knowledge-bases/1/query" -H "Content-Type: application/json" -d '{"question":"报销流程是什么？","top_k":3}' | cat

echo "\n[8/14] Tool list"
curl -sS "$API/api/tools" | cat

echo "\n[9/14] Agent chat with persistent audit"
curl -sS -X POST "$API/api/agents/1/chat" -H "Content-Type: application/json" -H "X-Tenant-Id: 1" -H "X-User-Role: admin" -d '{"question":"请调用知识库工具回答报销流程是什么？"}' | cat

echo "\n[10/14] Tool audit summary"
curl -sS "$API/api/audit/tools/summary" | cat

echo "\n[11/14] Tool audit records"
curl -sS "$API/api/audit/tools" | cat

echo "\n[12/14] Prompt list"
curl -sS "$API/api/prompts" | cat

echo "\n[13/14] Workflow run"
curl -sS -X POST "$API/api/workflows/1/run" -H "Content-Type: application/json" -d '{"input":{"question":"报销流程是什么？"}}' | cat

echo "\n[14/14] Eval run"
curl -sS -X POST "$API/api/evals/runs" -H "Content-Type: application/json" -d '{"dataset_id":1,"model":"demo-model"}' | cat

echo "\nAgentFlow-AI V4 persistent verification completed."
