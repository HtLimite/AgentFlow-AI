$ErrorActionPreference = "Stop"

$ApiUrl = if ($env:AGENTFLOW_API_URL) { $env:AGENTFLOW_API_URL } else { "http://localhost:8000" }

function Invoke-AgentFlowJson {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Path,
    [string]$Body
  )

  $uri = "$ApiUrl$Path"
  if ($Body) {
    return Invoke-RestMethod -Method $Method -Uri $uri -ContentType "application/json; charset=utf-8" -Body $Body
  }
  return Invoke-RestMethod -Method $Method -Uri $uri
}

function Assert-True {
  param(
    [Parameter(Mandatory = $true)][bool]$Condition,
    [Parameter(Mandatory = $true)][string]$Message
  )
  if (-not $Condition) {
    throw $Message
  }
}

Write-Host "[1/12] Health"
$health = Invoke-AgentFlowJson -Method GET -Path "/health"
Assert-True ($health.status -eq "ok") "health check failed"
Write-Host "PASS status=$($health.status) service=$($health.service)"

Write-Host "`n[2/12] Full system health"
$full = Invoke-AgentFlowJson -Method GET -Path "/api/system/health/full"
Assert-True ($full.status -eq "ok") "full system health failed"
Write-Host "PASS tools=$($full.counts.tools) eval_datasets=$($full.counts.eval_datasets) workflow_nodes=$($full.counts.workflow_nodes)"

Write-Host "`n[3/12] Dashboard summary"
$dashboard = Invoke-AgentFlowJson -Method GET -Path "/api/dashboard/summary"
Assert-True ($dashboard.calls_today -ge 0) "dashboard summary failed"
Write-Host "PASS calls=$($dashboard.calls_today) tokens=$($dashboard.tokens_today) source=$($dashboard.source)"

Write-Host "`n[4/12] Knowledge bases"
$bases = Invoke-AgentFlowJson -Method GET -Path "/api/knowledge-bases"
Assert-True ($bases.Count -ge 1) "knowledge base list is empty"
Write-Host "PASS count=$($bases.Count) first=$($bases[0].name)"

Write-Host "`n[5/12] Knowledge query"
$knowledge = Invoke-AgentFlowJson -Method POST -Path "/api/knowledge-bases/1/query" -Body '{"question":"报销流程是什么？","top_k":3}'
Assert-True ($knowledge.citations.Count -ge 1) "knowledge query returned no citations"
Write-Host "PASS citations=$($knowledge.citations.Count) strategy=$($knowledge.debug.strategy)"

Write-Host "`n[6/12] Tool list"
$tools = Invoke-AgentFlowJson -Method GET -Path "/api/tools"
Assert-True ($tools.Count -ge 4) "tool list is incomplete"
Write-Host "PASS count=$($tools.Count)"

Write-Host "`n[7/12] Agent chat with trace"
$agent = Invoke-AgentFlowJson -Method POST -Path "/api/agents/1/chat" -Body '{"question":"请调用知识库工具回答报销流程是什么？"}'
Assert-True ($agent.tool_calls.Count -ge 1) "agent chat returned no tool calls"
Assert-True ($agent.trace_id.Length -gt 0) "agent trace_id is empty"
Write-Host "PASS agent_id=$($agent.agent_id) trace=$($agent.trace_id) tool_calls=$($agent.tool_calls.Count)"

Write-Host "`n[8/12] Tool audit summary"
$auditSummary = Invoke-AgentFlowJson -Method GET -Path "/api/audit/tools/summary"
Assert-True ($auditSummary.total_calls -ge 1) "audit summary is empty"
Write-Host "PASS total=$($auditSummary.total_calls) success_rate=$($auditSummary.success_rate)"

Write-Host "`n[9/12] Tool audit records"
$auditRecords = Invoke-AgentFlowJson -Method GET -Path "/api/audit/tools"
Assert-True ($auditRecords.Count -ge 1) "audit records are empty"
Write-Host "PASS count=$($auditRecords.Count) first_tool=$($auditRecords[0].tool_name)"

Write-Host "`n[10/12] Prompt list"
$prompts = Invoke-AgentFlowJson -Method GET -Path "/api/prompts"
Assert-True ($prompts.Count -ge 1) "prompt list is empty"
Write-Host "PASS count=$($prompts.Count)"

Write-Host "`n[11/12] Workflow run"
$workflow = Invoke-AgentFlowJson -Method POST -Path "/api/workflows/1/run" -Body '{"input":{"question":"报销流程是什么？"}}'
Assert-True ($workflow.status -eq "success") "workflow run failed"
Write-Host "PASS status=$($workflow.status) node_runs=$($workflow.node_runs.Count) source=$($workflow.source)"

Write-Host "`n[12/12] Eval run"
$eval = Invoke-AgentFlowJson -Method POST -Path "/api/evals/runs" -Body '{"dataset_id":1,"model":"demo-model"}'
Assert-True ($eval.status -eq "completed") "eval run did not complete"
Write-Host "PASS id=$($eval.id) status=$($eval.status) score=$($eval.score) cases=$($eval.cases.Count) source=$($eval.source)"

Write-Host "`nAgentFlow-AI V3 local verification completed."
