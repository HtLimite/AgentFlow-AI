# 现阶段设计与验证说明

## 1. 当前阶段定位

AgentFlow-AI 当前从 **V4 工程增强态** 继续推进到 **V5 真实模型运行时增强态 / 本地持久化演示态**。

V5 的目标不是只做静态 Demo，而是补齐更接近真实 AI 应用的运行时能力：

```txt
OpenAI-Compatible Chat Provider
Provider SSE 流式输出
Provider Embedding
RAG + pgvector SQL + Rerank
Eval Judge 评分协议
模型运行时健康检查
15 步持久化验收脚本
```

推荐运行模式仍然是：

```txt
Docker：PostgreSQL / Redis / MinIO
uv：FastAPI 后端
pnpm：Next.js 前端
```

没有真实 API Key 时保留本地 fallback，保证项目可以稳定演示；配置真实供应商后，系统优先走真实 Provider。

## 2. V5 已增强设计

### 2.1 Chat Provider 与流式输出

`/api/chat/completions` 已支持 OpenAI-Compatible Provider 非流式调用。

`/api/chat/completions/stream` 已支持供应商 SSE 流式输出：

- 有启用的 chat 模型时，优先请求供应商 `/chat/completions` 且 `stream=true`。
- 没有供应商时，回退本地 fallback streaming。
- SSE 输出包含 `meta`、`delta`、`done`、`error` 类型。
- 调用完成后记录 token、latency、status 到观测日志。

### 2.2 Provider Embedding

RAG embedding 已从固定本地向量升级为 provider-first：

- 如果 Settings 中存在启用的 `embedding` 模型，则优先调用供应商 `/embeddings`。
- 如果供应商失败或未配置，则回退本地 deterministic embedding。
- 本地 fallback 统一为 1536 维，适配 `knowledge_chunk.embedding VECTOR(1536)`。
- metadata 中记录 `embedding_source`、`embedding_model`、`embedding_provider`、`embedding_error`。

### 2.3 Rerank 基础链路

RAG 查询流程变为：

```txt
query embedding → pgvector SQL 候选召回 → lexical/vector 混合打分 → rerank → 返回 citations
```

当前 rerank 是本地轻量实现，返回：

```txt
rerank_score
rerank_reason
```

后续可以替换为真实 rerank provider。

### 2.4 Eval Judge 评分协议

Eval 已从简单 term scoring 升级为 Judge 协议基础版：

```txt
judge_mode
matched_terms
total_terms
reason
citation_count
```

当前实现是 `heuristic_judge`，用于稳定本地验收。后续可以接真实 judge 模型。

### 2.5 模型运行时健康检查

新增接口：

```txt
GET /api/system/model-runtime/health
```

返回：

```txt
provider_chat
provider_streaming
provider_embedding
provider_rerank
local_fallback
local_rerank
heuristic_judge
```

## 3. 为什么仍然必须启动 Docker

V5 验收必须证明以下能力真实可用：

- PostgreSQL 可连接。
- pgvector extension 可用。
- `knowledge_chunk.embedding` 可以参与 SQL 检索。
- `tool_audit_log` 可以持久化审计记录。
- `llm_call_log` 可以记录 token、cost、latency、status。
- RBAC tenant 上下文可以写入审计记录。
- Redis / MinIO 基础设施保留，为后续异步任务和文件存储做准备。

所以只启动 Web/API 而不启动 Docker，只能证明页面和 fallback 能跑，不能证明 V5 工程增强成立。

## 4. 标准启动流程

### 4.1 拉取最新代码

```bash
git pull origin main
```

### 4.2 准备环境变量

首次运行：

```cmd
copy .env.example .env
```

PowerShell：

```powershell
Copy-Item .env.example .env
```

本地 uv 后端必须使用 localhost：

```txt
DATABASE_URL=postgresql+psycopg://agentflow:agentflow@localhost:5432/agentflow
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=localhost:9000
```

### 4.3 启动 Docker 基础设施

```cmd
scripts\dev-infra.cmd
```

等价命令：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
```

### 4.4 启动 uv 后端

```cmd
scripts\dev-api-uv.cmd
```

等价命令：

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4.5 启动前端

```bash
pnpm install
pnpm dev:web
```

## 5. 严格持久化验证

基础健康：

```bash
curl http://localhost:8000/health
```

持久化健康：

```bash
curl http://localhost:8000/api/system/persistence/health
```

模型运行时健康：

```bash
curl http://localhost:8000/api/system/model-runtime/health
```

RBAC 上下文：

```bash
curl http://localhost:8000/api/system/rbac/context -H "X-Tenant-Id: 1" -H "X-User-Role: admin"
```

## 6. 完整接口验收

Windows：

```cmd
scripts\verify-local.cmd
```

Git Bash / Linux / macOS：

```bash
bash scripts/verify-local.sh
```

当前脚本覆盖 15 步：

| 步骤 | 验证内容 |
|---|---|
| 1 | 后端健康检查 |
| 2 | 系统模块健康检查 |
| 3 | 严格持久化健康检查 |
| 4 | RBAC 上下文 |
| 5 | 模型运行时健康检查 |
| 6 | Dashboard 聚合 |
| 7 | 知识库列表 |
| 8 | 知识库 RAG 问答 |
| 9 | 工具列表 |
| 10 | Agent 工具调用与持久化审计 |
| 11 | 工具审计统计 |
| 12 | 工具审计记录 |
| 13 | Prompt 列表 |
| 14 | Workflow 运行 |
| 15 | Eval Judge 运行 |

## 7. 真实模型联调建议

1. 在 `/settings` 新增 OpenAI-Compatible 供应商，例如 DeepSeek、Qwen、Kimi 或自建中转。
2. 新增一个 `chat` 模型。
3. 新增一个 `embedding` 模型。
4. 到 `/chat` 测试真实回答。
5. 上传新文档后到 `/knowledge` 提问，观察 `query_embedding_source` 和 `strategy`。
6. 到 `/dashboard` 检查调用日志和 token 数据。

## 8. 页面验收顺序

推荐按下面顺序打开：

```txt
/demo
/showcase
/settings
/chat
/knowledge
/agents
/audit
/workflows
/evals
/dashboard
/verification
```

重点看：

- `/settings`：是否可以配置 `chat` 和 `embedding` 模型。
- `/chat`：真实 provider 是否能回答；没有 provider 时 fallback 是否稳定。
- `/knowledge`：RAG 结果 debug.strategy 是否进入 `pgvector_sql_rerank` 或 fallback 策略。
- `/evals`：case 结果是否包含 `judge_mode`、`matched_terms`、`total_terms`。
- `/verification`：系统模块是否包含 provider streaming、embedding、rerank、judge。

## 9. 当前边界

V5 已具备真实模型运行时基础能力，但仍不是完整生产级平台。

后续还可增强：

- 真实 Rerank Provider。
- 真实 LLM-as-Judge Provider。
- RBAC 对业务路由强制鉴权。
- 审计日志分页、筛选、导出。
- HTTP / SQL 工具生产级安全策略。
- 线上 Demo、截图、GIF、演示视频。

## 10. 面试表达口径

推荐表述：

```txt
AgentFlow-AI 是一个企业级 AI Agent / RAG / Workflow 平台的本地持久化演示版本。
V5 增强后，项目已具备 OpenAI-Compatible Chat 调用、Provider 流式输出、Provider Embedding、RAG + pgvector SQL + Rerank、Eval Judge 协议、工具调用审计持久化、React Flow 拖拽工作流画布和 15 步本地验收。
```

避免表述：

```txt
这是完整生产级平台。
Rerank 和 Judge 都已经是完整真实模型在线调用。
所有权限、审计、检索、模型评测都已经完全生产化。
```
