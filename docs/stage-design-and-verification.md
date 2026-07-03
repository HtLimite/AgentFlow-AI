# 阶段设计与验收说明

## 1. 当前阶段定位

当前阶段是 **V3 平台展示态 / 本地持久化演示态**。

这意味着项目不能只证明“页面能打开”或“内存 demo 能返回数据”，而要证明：

```txt
Docker 基础设施可启动
uv 后端可连接真实 PostgreSQL
核心接口优先走数据库持久化
前端页面能展示 V3 平台能力
构建、测试、验收脚本可运行
```

内存 fallback 仍然保留，但定位是开发兜底，不作为 V2/V3 主验收结论。

## 2. 总体设计

### 2.1 本地运行拓扑

```txt
Browser
  ↓
Next.js Web，本地 pnpm dev:web，localhost:3000
  ↓
FastAPI API，本地 uv run uvicorn，localhost:8000
  ↓
Docker 基础设施
  ├─ PostgreSQL + pgvector，localhost:5432
  ├─ Redis，localhost:6379
  └─ MinIO，localhost:9000 / 9001
```

### 2.2 为什么采用 Docker + uv 混合模式

| 部分 | 运行方式 | 原因 |
|---|---|---|
| PostgreSQL / Redis / MinIO | Docker | 模拟真实基础设施，验证持久化与服务依赖 |
| FastAPI | 本地 uv | 符合当前开发环境，便于热更新、调试、测试 |
| Next.js | 本地 pnpm | 便于页面开发与构建验证 |
| 内存 fallback | 代码兜底 | 数据库不可用时仍能演示，但不作为主验收 |

## 3. 模块设计

### 3.1 Knowledge / RAG

设计目标：

- 知识库、文档、切片优先进入数据库。
- 文档解析后生成 chunk。
- chunk 通过 Embedding 门面生成向量。
- 查询时优先使用数据库中的 chunk，返回 answer、citations、debug。
- 数据库不可用时 fallback 到内存 demo。

验收重点：

```txt
GET /api/knowledge-bases 能返回数据库知识库
POST /api/knowledge-bases/1/query 能返回 citations
debug.strategy 应优先体现 database_vector 这类数据库路径
```

### 3.2 Model Provider / Chat

设计目标：

- 模型供应商配置保存到数据库。
- API Key 加密保存、脱敏展示。
- Provider Adapter 支持 OpenAI-compatible 接口。
- Chat 优先调用已配置供应商，失败时 fallback 到本地 demo。

验收重点：

```txt
/settings 可新增供应商
/api/model-providers 可读取配置
/api/model-providers/{id}/test 可验证供应商可达性
/api/chat/completions 可返回 answer、usage、latency_ms
```

### 3.3 Agent / Tool Audit

设计目标：

- Agent 根据问题选择工具。
- 工具调用统一经过 ToolRegistry。
- 每次工具调用记录 trace_id、audit_id、输入、输出、状态、耗时。
- 前端 `/audit` 页面展示审计列表、统计和详情。

验收重点：

```txt
POST /api/agents/1/chat 返回 trace_id
返回的 tool_calls 中包含 audit_id、latency_ms、status
GET /api/audit/tools/summary 返回统计
GET /api/audit/tools 返回审计记录
```

### 3.4 Workflow Canvas

设计目标：

- `/workflows` 页面展示轻量可视化画布。
- 不引入 React Flow，先用轻量实现降低构建风险。
- 点击运行后展示节点执行状态和节点输出。
- 后端 workflow run 优先写入持久化运行记录。

验收重点：

```txt
/workflows 能打开
点击运行后节点状态变更
右侧或下方能看到 node_runs 输出
POST /api/workflows/1/run 返回 status=success
```

### 3.5 Prompt / Eval Compare

设计目标：

- Prompt 支持模板、版本、变量渲染。
- Eval 支持 dataset、case、run。
- `/evals` 页面支持三组模型或 Prompt 横向对比。

验收重点：

```txt
GET /api/prompts 返回 Prompt 列表
POST /api/evals/runs 返回 completed
/evals 点击运行三组对比后展示分数与逐题对比
```

### 3.6 Observability / Dashboard

设计目标：

- Chat 调用记录 token、cost、latency。
- Dashboard 优先从数据库聚合。
- 数据库不可用时 fallback 到内存统计。

验收重点：

```txt
GET /api/dashboard/summary 返回 calls_today、tokens_today、cost_today、avg_latency_ms
页面 /dashboard 可展示统计卡片
```

## 4. 数据库设计与初始化顺序

PostgreSQL 初始化脚本按文件名顺序执行：

```txt
deploy/postgres/001_init.sql
deploy/postgres/003_v2_persistence.sql
deploy/postgres/004_tenant_audit.sql
```

设计原则：

- `001_init.sql` 创建基础表和 pgvector 扩展。
- `003_v2_persistence.sql` 创建 V2 核心持久化表。
- `004_tenant_audit.sql` 最后执行租户和审计扩展，避免提前 ALTER 未创建表。

严格持久化检查接口：

```txt
GET /api/system/persistence/health
```

它会真实查询核心表，只有数据库连通且表存在时才返回：

```json
{
  "status": "ok",
  "mode": "persistent",
  "database": "connected"
}
```

## 5. 现阶段如何验证

### 5.1 拉取最新代码

```bash
git pull origin main
```

### 5.2 准备环境文件

首次运行：

```cmd
Copy-Item .env.example .env
```

确认 `.env` 是本地 uv 后端模式：

```txt
DATABASE_URL=postgresql+psycopg://agentflow:agentflow@localhost:5432/agentflow
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=localhost:9000
```

### 5.3 启动 Docker 基础设施

Windows：

```cmd
scripts\dev-infra.cmd
```

或：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
```

检查容器：

```bash
docker ps
```

必须看到：

```txt
agentflow-postgres
agentflow-redis
agentflow-minio
```

### 5.4 启动 uv 后端

Windows：

```cmd
scripts\dev-api-uv.cmd
```

或：

```bash
cd apps/api
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5.5 严格验证持久化

```bash
curl http://localhost:8000/api/system/persistence/health
```

判定标准：

```txt
status = ok
mode = persistent
database = connected
tables_checked 包含 knowledge_base、prompt_template、workflow_run、eval_run、llm_call_log 等核心表
```

如果这个接口失败，说明当前不是合格的 V2/V3 持久化验收状态。

### 5.6 执行接口验收脚本

Windows：

```cmd
scripts\verify-local.cmd
```

Linux / macOS / Git Bash：

```bash
bash scripts/verify-local.sh
```

当前脚本应覆盖 13 步：

```txt
1. /health
2. /api/system/health/full
3. /api/system/persistence/health
4. /api/dashboard/summary
5. /api/knowledge-bases
6. /api/knowledge-bases/1/query
7. /api/tools
8. /api/agents/1/chat
9. /api/audit/tools/summary
10. /api/audit/tools
11. /api/prompts
12. /api/workflows/1/run
13. /api/evals/runs
```

### 5.7 启动前端页面验收

```bash
pnpm dev:web
```

打开：

```txt
http://localhost:3000/demo
http://localhost:3000/showcase
http://localhost:3000/dashboard
http://localhost:3000/knowledge
http://localhost:3000/agents
http://localhost:3000/workflows
http://localhost:3000/audit
http://localhost:3000/evals
http://localhost:3000/verification
```

### 5.8 构建与测试

```bash
pnpm --filter @agentflow/web build
cd apps/api
uv run python -m compileall app
uv run python -m pytest
```

## 6. 验收结论模板

完成后可以这样记录：

```txt
V3 阶段验收通过：
- Docker 基础设施 postgres / redis / minio 已启动。
- uv 后端连接 localhost PostgreSQL 成功。
- /api/system/persistence/health 返回 persistent。
- 13 步接口验收通过。
- /demo、/workflows、/audit、/evals、/verification 页面可用。
- 前端 build、后端 compileall、pytest 通过。
```

## 7. 不通过时优先排查

| 现象 | 优先排查 |
|---|---|
| `/health` 失败 | uv 后端是否启动，8000 是否被占用 |
| `/persistence/health` 失败 | Docker Desktop、Postgres 容器、`.env` 的 localhost 地址 |
| 表不存在 | 是否新库初始化失败，必要时删除旧 volume 后重建 |
| Settings 保存失败 | DATABASE_URL 是否仍是 `postgres:5432` |
| 页面空白 | `NEXT_PUBLIC_API_BASE_URL`、前端 dev server、浏览器控制台 |
| build 失败 | TypeScript typed routes、Link href 类型、组件 import |

## 8. 当前边界

现阶段可以作为本地持久化演示态，但还不是完整生产级平台：

- Workflow 画布是轻量展示，不是真 React Flow 拖拽编排。
- 工具审计当前以演示链路为主，后续应持久化、分页、筛选、导出。
- Embedding 仍有本地确定性向量 fallback，真实 pgvector 相似度 SQL 检索属于后续增强。
- RBAC、多租户隔离、生产级安全策略仍需 V4/V5 继续补齐。
