@echo off
setlocal
if "%AGENTFLOW_API_URL%"=="" set AGENTFLOW_API_URL=http://localhost:8000

echo [1/6] Health
curl -sS "%AGENTFLOW_API_URL%/health"

echo.
echo [2/6] Full system health
curl -sS "%AGENTFLOW_API_URL%/api/system/health/full"

echo.
echo [3/6] Knowledge query
curl -sS -X POST "%AGENTFLOW_API_URL%/api/knowledge-bases/1/query" -H "Content-Type: application/json" -d "{\"question\":\"报销流程是什么？\",\"top_k\":3}"

echo.
echo [4/6] Tool list
curl -sS "%AGENTFLOW_API_URL%/api/tools"

echo.
echo [5/6] Agent chat
curl -sS -X POST "%AGENTFLOW_API_URL%/api/agents/1/chat" -H "Content-Type: application/json" -d "{\"question\":\"请调用知识库工具回答报销流程是什么？\"}"

echo.
echo [6/6] Eval run
curl -sS -X POST "%AGENTFLOW_API_URL%/api/evals/runs" -H "Content-Type: application/json" -d "{\"dataset_id\":1,\"model\":\"demo-model\"}"

echo.
echo AgentFlow-AI local verification completed.
endlocal
