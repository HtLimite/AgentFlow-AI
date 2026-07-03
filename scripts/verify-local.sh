#!/usr/bin/env bash
set -euo pipefail
API="${AGENTFLOW_API_URL:-http://localhost:8000}"

echo "[1/12] Health"
curl -sS "$API/health" | cat

echo "\n[2/12] Full system health"
curl -sS "$API/api/system/health/full" | cat

echo "\n[3/12] Dashboard summary"
curl -sS "$API/api/dashboard/summary" | cat

echo "\n[4/12] Knowledge bases"
curl -sS "$API/api/knowledge-bases" | cat

echo "\n[5/12] Knowledge query"
curl -sS -X POST "$API/api/knowledge-bases/1/query" -H "Content-Type: application/json" -d '{"question":"报销流程是什么？","top_k":3}' | cat

echo "\n[6/12] Tool list"
curl -sS "$API/api/tools" | cat

echo "\n[7/12] Agent chat with trace"
curl -sS -X POST "$API/api/agents/1/chat" -H "Content-Type: application/json" -d '{"question":"请调用知识库工具回答报销流程是什么？"}' | cat

echo "\n[8/12] Tool audit summary"
curl -sS "$API/api/audit/tools/summary" | cat

echo "\n[9/12] Tool audit records"
curl -sS "$API/api/audit/tools" | cat

echo "\n[10/12] Prompt list"
curl -sS "$API/api/prompts" | cat

echo "\n[11/12] Workflow run"
curl -sS -X POST "$API/api/workflows/1/run" -H "Content-Type: application/json" -d '{"input":{"question":"报销流程是什么？"}}' | cat

echo "\n[12/12] Eval run"
curl -sS -X POST "$API/api/evals/runs" -H "Content-Type: application/json" -d '{"dataset_id":1,"model":"demo-model"}' | cat

echo "\nAgentFlow-AI V3 local verification completed."
