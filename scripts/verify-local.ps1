$ErrorActionPreference = "Stop"

[Console]::InputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

$ApiUrl = if ($env:AGENTFLOW_API_URL) { $env:AGENTFLOW_API_URL } else { "http://localhost:8000" }
$VerifyQuestion = if ($env:AGENTFLOW_VERIFY_QUESTION) { $env:AGENTFLOW_VERIFY_QUESTION } else { "请根据当前知识库内容回答。" }

Add-Type -AssemblyName System.Net.Http
$script:HttpClient = [System.Net.Http.HttpClient]::new()
$script:HttpClient.DefaultRequestHeaders.Accept.Clear()
[void]$script:HttpClient.DefaultRequestHeaders.Accept.Add([System.Net.Http.Headers.MediaTypeWithQualityHeaderValue]::new("application/json"))

function ConvertTo-AgentFlowJson {
  param([Parameter(Mandatory = $true)]$Value)
  return ($Value | ConvertTo-Json -Depth 20 -Compress)
}

function Invoke-AgentFlowJson {
  param(
    [Parameter(Mandatory = $true)][string]$Method,
    [Parameter(Mandatory = $true)][string]$Path,
    [string]$Body,
    [hashtable]$Headers
  )

  $uri = "$ApiUrl$Path"
  $request = [System.Net.Http.HttpRequestMessage]::new([System.Net.Http.HttpMethod]::new($Method), $uri)
  if ($Headers) {
    foreach ($key in $Headers.Keys) {
      [void]$request.Headers.TryAddWithoutValidation($key, [string]$Headers[$key])
    }
  }
  if ($Body) {
    $request.Content = [System.Net.Http.StringContent]::new($Body, [System.Text.Encoding]::UTF8, "application/json")
  }

  $response = $script:HttpClient.SendAsync($request).GetAwaiter().GetResult()
  $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
  $text = [System.Text.Encoding]::UTF8.GetString($bytes)
  if (-not $response.IsSuccessStatusCode) {
    throw "HTTP $([int]$response.StatusCode) $($response.ReasonPhrase): $text"
  }
  if ([string]::IsNullOrWhiteSpace($text)) {
    return $null
  }
  return $text | ConvertFrom-Json
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

function Get-Count {
  param($Value)
  if ($null -eq $Value) { return 0 }
  return $Value.Count
}

Write-Host "[1/14] Health"
$health = Invoke-AgentFlowJson -Method GET -Path "/health"
Assert-True ($health.status -eq "ok") "health check failed"
Write-Host "PASS status=$($health.status) service=$($health.service)"

Write-Host "`n[2/14] Full system health"
$full = Invoke-AgentFlowJson -Method GET -Path "/api/system/health/full"
Assert-True ($full.status -eq "ok") "full system health failed: $($full.failed_modules -join ', ')"
Assert-True ($full.modules.react_flow_canvas -eq $true) "react flow canvas module missing"
Assert-True ($full.modules.rbac -eq $true) "rbac module missing"
Write-Host "PASS tools=$($full.counts.tools) eval_datasets=$($full.counts.eval_datasets) workflow_nodes=$($full.counts.workflow_nodes)"

Write-Host "`n[3/14] Persistence health"
$persistence = Invoke-AgentFlowJson -Method GET -Path "/api/system/persistence/health"
Assert-True ($persistence.status -eq "ok") "persistence health failed"
Assert-True ($persistence.mode -eq "persistent") "not running in persistent mode"
Assert-True ($persistence.database -eq "connected") "database is not connected"
Assert-True ($persistence.tables_checked -contains "tool_audit_log") "tool_audit_log table missing"
Write-Host "PASS mode=$($persistence.mode) database=$($persistence.database) tables=$($persistence.tables_checked.Count)"

Write-Host "`n[4/14] RBAC context"
$rbacHeaders = @{ "X-Tenant-Id" = "1"; "X-User-Role" = "admin" }
$rbac = Invoke-AgentFlowJson -Method GET -Path "/api/system/rbac/context" -Headers $rbacHeaders
Assert-True ($rbac.status -eq "ok") "rbac context failed"
Assert-True ($rbac.context.permissions.Count -ge 1) "rbac permissions empty"
Write-Host "PASS tenant=$($rbac.context.tenant_id) role=$($rbac.context.role)"

Write-Host "`n[5/14] Dashboard summary"
$dashboard = Invoke-AgentFlowJson -Method GET -Path "/api/dashboard/summary"
Assert-True ($dashboard.calls_today -ge 0) "dashboard summary failed"
Write-Host "PASS calls=$($dashboard.calls_today) tokens=$($dashboard.tokens_today) source=$($dashboard.source)"

Write-Host "`n[6/14] Runtime resources"
$bases = Invoke-AgentFlowJson -Method GET -Path "/api/knowledge-bases"
$agents = Invoke-AgentFlowJson -Method GET -Path "/api/agents"
$workflows = Invoke-AgentFlowJson -Method GET -Path "/api/workflows"
$models = Invoke-AgentFlowJson -Method GET -Path "/api/model-providers/models/list"
Assert-True ($bases.Count -ge 1) "knowledge base list is empty"
Assert-True ($agents.Count -ge 1) "agent list is empty"
Assert-True ($workflows.Count -ge 1) "workflow list is empty"
$kbId = [int]$bases[0].id
$agentId = [int]$agents[0].id
$workflowId = [int]$workflows[0].id
$chatModels = @($models | Where-Object { $_.enabled -eq $true -and $_.model_type -eq "chat" })
$chatModel = if ($env:AGENTFLOW_VERIFY_MODEL) { $env:AGENTFLOW_VERIFY_MODEL } elseif ($chatModels.Count -gt 0) { [string]$chatModels[0].model_name } else { $null }
Write-Host "PASS kb_id=$kbId agent_id=$agentId workflow_id=$workflowId model=$chatModel"

Write-Host "`n[7/14] Chat completion"
$chatPayload = @{ temperature = 0.7; messages = @(@{ role = "user"; content = "你好" }) }
if ($chatModel) { $chatPayload.model = $chatModel }
$chat = Invoke-AgentFlowJson -Method POST -Path "/api/chat/completions" -Body (ConvertTo-AgentFlowJson $chatPayload)
Assert-True ($chat.answer.Length -gt 0) "chat returned empty answer"
Write-Host "PASS mode=$($chat.mode) provider=$($chat.provider) model=$($chat.model)"

Write-Host "`n[8/14] Knowledge query"
$knowledgeBody = ConvertTo-AgentFlowJson @{ question = $VerifyQuestion; top_k = 3 }
$knowledge = Invoke-AgentFlowJson -Method POST -Path "/api/knowledge-bases/$kbId/query" -Body $knowledgeBody
$citationCount = Get-Count $knowledge.citations
Assert-True ($null -ne $knowledge.answer -and $knowledge.answer.Length -gt 0) "knowledge query returned empty answer"
Write-Host "PASS kb_id=$kbId citations=$citationCount source=$($knowledge.source)"

Write-Host "`n[9/14] Tool list"
$tools = Invoke-AgentFlowJson -Method GET -Path "/api/tools"
Assert-True ($tools.Count -ge 4) "tool list is incomplete"
Write-Host "PASS count=$($tools.Count)"

Write-Host "`n[10/14] Agent chat with persistent audit"
$agentBody = ConvertTo-AgentFlowJson @{ question = $VerifyQuestion }
$agent = Invoke-AgentFlowJson -Method POST -Path "/api/agents/$agentId/chat" -Headers $rbacHeaders -Body $agentBody
Assert-True ($agent.tool_calls.Count -ge 1) "agent chat returned no tool calls"
Assert-True ($agent.trace_id.Length -gt 0) "agent trace_id is empty"
Assert-True ($agent.tool_calls[0].persistent_audit_id -ge 1) "persistent audit id missing"
Write-Host "PASS agent_id=$($agent.agent_id) trace=$($agent.trace_id) persistent_audit_id=$($agent.tool_calls[0].persistent_audit_id)"

Write-Host "`n[11/14] Tool audit summary"
$auditSummary = Invoke-AgentFlowJson -Method GET -Path "/api/audit/tools/summary"
Assert-True ($auditSummary.total_calls -ge 1) "audit summary is empty"
Assert-True ($auditSummary.source -eq "database") "audit summary is not database backed"
Write-Host "PASS total=$($auditSummary.total_calls) success_rate=$($auditSummary.success_rate) source=$($auditSummary.source)"

Write-Host "`n[12/14] Tool audit records"
$auditRecords = Invoke-AgentFlowJson -Method GET -Path "/api/audit/tools"
Assert-True ($auditRecords.Count -ge 1) "audit records are empty"
Assert-True ($auditRecords[0].source -eq "database") "audit records are not database backed"
Write-Host "PASS count=$($auditRecords.Count) first_tool=$($auditRecords[0].tool_name)"

Write-Host "`n[13/14] Workflow run"
$workflowBody = ConvertTo-AgentFlowJson @{ input = @{ question = $VerifyQuestion } }
$workflow = Invoke-AgentFlowJson -Method POST -Path "/api/workflows/$workflowId/run" -Body $workflowBody
Assert-True ($workflow.status -eq "success") "workflow run failed"
Write-Host "PASS workflow_id=$workflowId status=$($workflow.status) node_runs=$($workflow.node_runs.Count) source=$($workflow.source)"

Write-Host "`n[14/14] Eval run"
$evalBody = ConvertTo-AgentFlowJson @{ dataset_id = 1; model = $(if ($chatModel) { $chatModel } else { "local-rag-evaluator" }) }
$eval = Invoke-AgentFlowJson -Method POST -Path "/api/evals/runs" -Body $evalBody
Assert-True ($eval.status -eq "completed") "eval run did not complete"
Write-Host "PASS id=$($eval.id) status=$($eval.status) score=$($eval.score) cases=$($eval.cases.Count) source=$($eval.source)"

Write-Host "`nAgentFlow-AI runtime verification completed."
