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

Write-Host "[1/6] Health"
$health = Invoke-AgentFlowJson -Method GET -Path "/health"
Assert-True ($health.status -eq "ok") "health check failed"
Write-Host "PASS status=$($health.status) service=$($health.service)"

Write-Host "`n[2/6] Full system health"
$full = Invoke-AgentFlowJson -Method GET -Path "/api/system/health/full"
Assert-True ($full.status -eq "ok") "full system health failed"
Write-Host "PASS modules=dashboard,model_provider,chat,knowledge_base,agent_tools,workflow,prompt,eval,observability knowledge_bases=$($full.counts.knowledge_bases) tools=$($full.counts.tools) eval_datasets=$($full.counts.eval_datasets) workflow_nodes=$($full.counts.workflow_nodes)"

Write-Host "`n[3/6] Knowledge query"
$knowledge = Invoke-AgentFlowJson -Method POST -Path "/api/knowledge-bases/1/query" -Body '{"question":"\u62a5\u9500\u6d41\u7a0b\u662f\u4ec0\u4e48\uff1f","top_k":3}'
Assert-True ($knowledge.citations.Count -ge 1) "knowledge query returned no citations"
Write-Host "PASS citations=$($knowledge.citations.Count) strategy=$($knowledge.debug.strategy) top_k=$($knowledge.debug.top_k) first_score=$($knowledge.citations[0].score) first_document=$($knowledge.citations[0].document)"

Write-Host "`n[4/6] Tool list"
$tools = Invoke-AgentFlowJson -Method GET -Path "/api/tools"
Assert-True ($tools.Count -ge 4) "tool list is incomplete"
$toolNames = ($tools | ForEach-Object { $_.name }) -join ","
Write-Host "PASS count=$($tools.Count) tools=$toolNames"

Write-Host "`n[5/6] Agent chat"
$agent = Invoke-AgentFlowJson -Method POST -Path "/api/agents/1/chat" -Body '{"question":"\u8bf7\u8c03\u7528\u77e5\u8bc6\u5e93\u5de5\u5177\u56de\u7b54\u62a5\u9500\u6d41\u7a0b\u662f\u4ec0\u4e48\uff1f"}'
Assert-True ($agent.tool_calls.Count -ge 1) "agent chat returned no tool calls"
Write-Host "PASS agent_id=$($agent.agent_id) tool_calls=$($agent.tool_calls.Count) first_tool=$($agent.tool_calls[0].tool_name) status=$($agent.tool_calls[0].status)"

Write-Host "`n[6/6] Eval run"
$eval = Invoke-AgentFlowJson -Method POST -Path "/api/evals/runs" -Body '{"dataset_id":1,"model":"demo-model"}'
Assert-True ($eval.status -eq "completed") "eval run did not complete"
Write-Host "PASS id=$($eval.id) status=$($eval.status) score=$($eval.score) cases=$($eval.cases.Count)"

Write-Host "`nAgentFlow-AI local verification completed."
