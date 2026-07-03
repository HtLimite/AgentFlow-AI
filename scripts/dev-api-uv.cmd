@echo off
setlocal
cd apps\api
echo Starting AgentFlow-AI API with uv...
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
endlocal
