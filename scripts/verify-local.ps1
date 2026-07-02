$ErrorActionPreference = "Stop"

$ApiUrl = if ($env:AGENTFLOW_API_URL) { $env:AGENTFLOW_API_URL } else { "http://localhost:8000" }
$OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

function Invoke-AgentFlowJson {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Path,
    [string]$Body
  )

  $uri = "$ApiUrl$Path"
  if ($Body) {
    Invoke-RestMethod -Method $Method -Uri $uri -ContentType "application/json; charset=utf-8" -Body $Body | ConvertTo-Json -Depth 12 -Compress
  } else {
    Invoke-RestMethod -Method $Method -Uri $uri | ConvertTo-Json -Depth 12 -Compress
  }
}

Write-Host "[1/6] Health"
Invoke-AgentFlowJson -Method GET -Path "/health"

Write-Host "`n[2/6] Full system health"
Invoke-AgentFlowJson -Method GET -Path "/api/system/health/full"

Write-Host "`n[3/6] Knowledge query"
Invoke-AgentFlowJson -Method POST -Path "/api/knowledge-bases/1/query" -Body '{"question":"\u62a5\u9500\u6d41\u7a0b\u662f\u4ec0\u4e48\uff1f","top_k":3}'

Write-Host "`n[4/6] Tool list"
Invoke-AgentFlowJson -Method GET -Path "/api/tools"

Write-Host "`n[5/6] Agent chat"
Invoke-AgentFlowJson -Method POST -Path "/api/agents/1/chat" -Body '{"question":"\u8bf7\u8c03\u7528\u77e5\u8bc6\u5e93\u5de5\u5177\u56de\u7b54\u62a5\u9500\u6d41\u7a0b\u662f\u4ec0\u4e48\uff1f"}'

Write-Host "`n[6/6] Eval run"
Invoke-AgentFlowJson -Method POST -Path "/api/evals/runs" -Body '{"dataset_id":1,"model":"demo-model"}'

Write-Host "`nAgentFlow-AI local verification completed."
