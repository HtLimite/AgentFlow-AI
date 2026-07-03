# 现阶段设计与验证说明

## 1. 当前阶段定位

AgentFlow-AI 当前从 **V3 平台展示态 / 本地持久化演示态** 继续增强到 **V4 工程增强态**。

V4 的目标不是继续做静态 Demo，而是补齐更接近真实产品的关键工程能力：

```txt
React Flow 真拖拽画布
工具调用审计数据库持久化
pgvector SQL 相似度检索
多租户 RBAC 上下文
持久化验收脚本增强
```

推荐运行模式仍然是：

```txt
Docker：PostgreSQL / Redis / MinIO
uv：FastAPI 后端
pnpm：Next.js 前端
```

内存 fallback 仍保留，但只作为数据库不可用时的降级兜底，不能作为 V2/V3/V4 的主要验收结论。

## 2. V4 已增强设计

### 2.1 React Flow 真拖拽画布

`/workflows` 已从 V3 的轻量静态画布升级为 React Flow 画布：

- 支持节点拖拽。
- 支持节点连线。
- 支持新增 HTTP 节点。
- 支持根据当前节点和边生成 workflow definition。
- 支持运行当前画布并展示节点输出。
- 支持节点选中、运行状态高亮、MiniMap、Controls。

### 2.2 工具调用审计数据库持久化

V3 的审计记录主要是内存态。V4 新增 `tool_audit_log` 表，并新增数据库优先的审计服务。

核心字段：

```txt
trace_id
agent_id
tool_name
input_json
output_json
status
latency_ms
error_message
tenant_id
created_at
```

Agent 调用工具后，会把每次 tool call 写入数据库，并在响应中返回：

```txt
trace_id
audit_id
persistent_audit_id
latency_ms
```

`/api/audit/tools` 和 `/api/audit/tools/summary` 优先读取数据库，数据库不可用时才 fallback 到内存审计。

### 2.3 pgvector SQL 相似度检索

V4 将知识库检索从 metadata 内的模拟向量逐步升级为 pgvector SQL 检索。

新增能力：

- 文档切片写入时同步写入 `knowledge_chunk.embedding`。
- 查询时优先使用 SQL：`embedding <=> query_embedding`。
- 返回结果中保留 `vector_score`、`lexical_score`、`strategy`。
- 如果历史数据没有 embedding，则 fallback 到 metadata hybrid 检索。

期望策略字段：

```txt
pgvector_sql_hybrid
```

历史数据 fallback 可能返回：

```txt
metadata_vector_hybrid
```

### 2.4 多租户 RBAC 基础

新增轻量 RBAC 上下文，基于请求头传入：

```txt
X-Tenant-Id
X-User-Id
X-User-Role
```

当前内置角色：

| 角色 | 用途 |
|---|---|
| owner | 全权限 |
| admin | 管理员 |
| operator | 运营人员 |
| viewer | 只读/可运行部分能力 |

验证接口：

```txt
GET /api/system/rbac/context
```

Agent 工具调用审计写库时会带上 `tenant_id`。

## 3. 为什么必须启动 Docker

V4 验收必须证明以下能力真实可用：

- PostgreSQL 可连接。
- pgvector extension 可用。
- `knowledge_chunk.embedding` 可以参与 SQL 检索。
- `tool_audit_log` 可以持久化审计记录。
- RBAC tenant 上下文可以写入审计记录。
- Redis / MinIO 基础设施保留，为后续异步任务和文件存储做准备。

所以只启动 Web/API 而不启动 Docker，只能证明页面和 fallback 能跑，不能证明 V4 工程增强成立。

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

检查：

```bash
docker ps
```

必须看到：

```txt
agentflow-postgres
agentflow-redis
agentflow-minio
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

期望：

```json
{
  "status": "ok",
  "mode": "persistent",
  "database": "connected"
}
```

同时 `tables_checked` 中应该包含：

```txt
tool_audit_log
tenant
audit_log
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

当前脚本覆盖 14 步：

| 步骤 | 验证内容 |
|---|---|
| 1 | 后端健康检查 |
| 2 | 系统模块健康检查 |
| 3 | 严格持久化健康检查 |
| 4 | RBAC 上下文 |
| 5 | Dashboard 聚合 |
| 6 | 知识库列表 |
| 7 | 知识库 RAG 问答 |
| 8 | 工具列表 |
| 9 | Agent 工具调用与持久化审计 |
| 10 | 工具审计统计 |
| 11 | 工具审计记录 |
| 12 | Prompt 列表 |
| 13 | Workflow 运行 |
| 14 | Eval 评测运行 |

## 7. 页面验收顺序

推荐按下面顺序打开：

```txt
/demo
/showcase
/knowledge
/agents
/audit
/workflows
/evals
/dashboard
/verification
```

重点看：

- `/workflows`：是否为 React Flow 画布，节点是否可拖拽、可连线、可新增 HTTP 节点。
- `/agents`：是否返回 `trace_id`、`audit_id`、`persistent_audit_id`。
- `/audit`：审计数据 source 是否来自 database。
- `/knowledge`：RAG 结果 debug.strategy 是否优先出现 `pgvector_sql_hybrid`。
- `/verification`：系统模块是否包含 `react_flow_canvas` 和 `rbac`。

## 8. 构建与测试验收

前端构建：

```bash
pnpm --filter @agentflow/web build
```

后端编译与测试：

```bash
cd apps/api
uv run python -m compileall app
uv run python -m pytest
```

## 9. 常见问题判断

### 9.1 `/health` 通过，但 `/api/system/persistence/health` 失败

说明 API 进程启动了，但数据库没有连上或表结构没初始化。

处理：

```cmd
scripts\dev-infra.cmd
scripts\dev-api-uv.cmd
```

### 9.2 后端连接 `postgres:5432` 失败

本地 uv 后端运行在宿主机，不在 Docker 网络里，所以不能用 `postgres` 作为主机名。

应改为：

```txt
DATABASE_URL=postgresql+psycopg://agentflow:agentflow@localhost:5432/agentflow
```

### 9.3 React Flow 构建失败

先安装依赖：

```bash
pnpm install
```

再构建：

```bash
pnpm build:web
```

### 9.4 pgvector 策略没有出现

可能是旧数据没有写入 `embedding` 列。新上传文档后再查询，或重建开发数据库卷后重新启动基础设施。

## 10. 当前边界

V4 已经具备更强工程展示能力，但仍不是完整生产级平台。

后续还可增强：

- 审计日志分页、筛选、导出。
- RBAC 对每个业务路由强制鉴权。
- 真实 Embedding Provider 与真实 rerank。
- React Flow 节点配置面板更细化。
- 线上 Demo、截图、GIF、演示视频。

## 11. 面试表达口径

推荐表述：

```txt
AgentFlow-AI 是一个企业级 AI Agent / RAG / Workflow 平台的本地持久化演示版本。
V4 增强后，项目已具备 React Flow 拖拽工作流画布、工具调用审计数据库持久化、pgvector SQL 检索基础能力、多租户 RBAC 上下文和 14 步持久化验收脚本。
```

避免表述：

```txt
这是完整生产级平台。
所有权限、审计、检索、模型评测都已经完全生产化。
```
