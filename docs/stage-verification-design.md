# 现阶段设计与验证说明

## 1. 当前阶段定位

AgentFlow-AI 当前处于 **V3 平台展示态 / 本地持久化演示态**。

这不是纯内存 Demo。当前推荐运行模式是：

```txt
Docker：PostgreSQL / Redis / MinIO
uv：FastAPI 后端
pnpm：Next.js 前端
```

内存 fallback 仍保留，但只作为数据库不可用时的降级兜底，不能作为 V2/V3 的主要验收结论。

## 2. 为什么必须启动 Docker

V2/V3 的核心变化是把 V1/V1.5 的演示链路升级为数据库优先：

- Knowledge Base、Document、Chunk 需要数据库表支撑。
- Prompt Template / Prompt Version 需要持久化。
- Workflow Definition / Workflow Run / Node Run 需要持久化。
- Eval Dataset / Eval Case / Eval Run 需要持久化。
- Dashboard 需要从调用日志和运行数据聚合。
- MinIO 为后续真实文件存储预留。
- Redis 为后续任务队列、缓存和异步工作流预留。

因此只启动 Web/API 而不启动 Docker 基础设施，只能证明页面和 fallback 能跑，不能证明 V2/V3 的工程化能力成立。

## 3. 当前模块设计

### 3.1 前端层

前端基于 Next.js，页面按平台模块组织：

| 页面 | 作用 |
|---|---|
| `/demo` | V3 演示动线页 |
| `/showcase` | 作品展示页 |
| `/dashboard` | 调用量、Token、耗时、失败率看板 |
| `/settings` | 模型供应商配置 |
| `/chat` | Chat Playground |
| `/knowledge` | 知识库上传、切片、RAG 问答 |
| `/agents` | Agent 工具调用链路 |
| `/workflows` | V3 轻量工作流画布 |
| `/audit` | 工具调用审计控制台 |
| `/prompts` | Prompt 模板与变量渲染 |
| `/evals` | Prompt / Eval 对比中心 |
| `/verification` | 系统体检与验收中心 |

### 3.2 后端层

后端基于 FastAPI，按业务域拆路由：

| 路由 | 作用 |
|---|---|
| `/api/system` | 系统健康、持久化健康、验收计划 |
| `/api/model-providers` | 模型供应商配置与连接测试 |
| `/api/chat` | Chat Completion 和流式接口骨架 |
| `/api/knowledge-bases` | 知识库、文档、RAG 查询 |
| `/api/agents` | Agent 对话与工具调用 |
| `/api/tools` | 工具列表与工具调试 |
| `/api/audit` | 工具调用审计 |
| `/api/workflows` | 工作流定义与运行 |
| `/api/prompts` | Prompt 模板、版本、渲染 |
| `/api/evals` | 评测集与评测运行 |
| `/api/dashboard` | 看板聚合数据 |

### 3.3 持久化层

当前数据库初始化脚本按顺序执行：

```txt
deploy/postgres/001_init.sql
deploy/postgres/003_v2_persistence.sql
deploy/postgres/004_tenant_audit.sql
```

核心表包括：

```txt
ai_model_provider
knowledge_base
knowledge_document
knowledge_chunk
prompt_template
prompt_version
workflow_definition
workflow_run
workflow_node_run
eval_dataset
eval_case
eval_run
llm_call_log
```

`GET /api/system/persistence/health` 会真实查询这些表，返回 `mode=persistent` 才说明数据库链路可用。

## 4. 当前验证目标

现阶段验证不只是“页面能打开”，而是验证以下四件事：

1. Docker 基础设施能启动。
2. uv 后端能连接 Docker PostgreSQL。
3. 严格持久化健康检查通过。
4. V3 页面与接口能跑通主链路。

## 5. 标准启动流程

### 5.1 拉取最新代码

```bash
git pull origin main
```

### 5.2 准备环境变量

首次运行：

```cmd
copy .env.example .env
```

PowerShell：

```powershell
Copy-Item .env.example .env
```

关键配置应使用 localhost：

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

等价命令：

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

等价命令：

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5.5 启动前端

```bash
pnpm dev:web
```

## 6. 严格持久化验证

先验证基础健康：

```bash
curl http://localhost:8000/health
```

再验证持久化健康：

```bash
curl http://localhost:8000/api/system/persistence/health
```

期望结果：

```json
{
  "status": "ok",
  "mode": "persistent",
  "database": "connected"
}
```

如果这个接口失败，说明当前不是合格的 V2/V3 持久化验收状态。

## 7. 完整接口验收

Windows：

```cmd
scripts\verify-local.cmd
```

Git Bash / Linux / macOS：

```bash
bash scripts/verify-local.sh
```

当前脚本覆盖 13 步：

| 步骤 | 验证内容 |
|---|---|
| 1 | 后端健康检查 |
| 2 | 系统模块健康检查 |
| 3 | 严格持久化健康检查 |
| 4 | Dashboard 聚合 |
| 5 | 知识库列表 |
| 6 | 知识库 RAG 问答 |
| 7 | 工具列表 |
| 8 | Agent 工具调用与 trace |
| 9 | 工具审计统计 |
| 10 | 工具审计记录 |
| 11 | Prompt 列表 |
| 12 | Workflow 运行 |
| 13 | Eval 评测运行 |

## 8. 页面验收顺序

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

验收重点：

- `/demo`：能讲清楚项目演示动线。
- `/knowledge`：可以看到知识库问答和引用来源。
- `/agents`：Agent 返回 `trace_id` 和工具调用结果。
- `/audit`：能看到工具调用审计记录。
- `/workflows`：能看到轻量工作流画布和节点输出。
- `/evals`：能运行三组 Prompt/Eval 对比。
- `/verification`：系统体检能展示 V3 模块状态。

## 9. 构建与测试验收

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

## 10. 常见问题判断

### 10.1 `/health` 通过，但 `/api/system/persistence/health` 失败

说明 API 进程启动了，但数据库没有连上或表结构没初始化。

处理顺序：

```cmd
scripts\dev-infra.cmd
scripts\dev-api-uv.cmd
```

再重新请求：

```bash
curl http://localhost:8000/api/system/persistence/health
```

### 10.2 后端连接 `postgres:5432` 失败

本地 uv 后端运行在宿主机，不在 Docker 网络里，所以不能用 `postgres` 作为主机名。

应改为：

```txt
DATABASE_URL=postgresql+psycopg://agentflow:agentflow@localhost:5432/agentflow
```

只有完整 Docker 模式下，API 容器才使用 `postgres`、`redis`、`minio` 这些 service name。

### 10.3 接口返回 fallback 或 local_vector

说明当前链路可能没有真正使用数据库优先能力。先确认：

```bash
curl http://localhost:8000/api/system/persistence/health
```

如果持久化健康通过，再检查具体模块是否还处于演示降级路径。

## 11. 当前边界

当前阶段可以作为求职作品和本地演示平台，但不要表述为完整生产级平台。

仍需后续增强：

- React Flow 真拖拽工作流画布。
- 审计日志数据库持久化、筛选、分页、导出。
- 真实 pgvector 相似度 SQL 检索。
- 更完整的模型流式输出。
- 多租户 RBAC 页面。
- 线上 Demo、截图、GIF、演示视频。

## 12. 面试表达口径

推荐表述：

```txt
AgentFlow-AI 是一个企业级 AI Agent / RAG / Workflow 平台的本地持久化演示版本。
当前通过 Docker 启动 PostgreSQL、Redis、MinIO，通过 uv 启动 FastAPI 后端，通过 Next.js 提供管理台。
项目已跑通模型供应商配置、知识库 RAG、Agent 工具调用、工具审计、轻量工作流画布、Prompt 管理、Eval 对比、Dashboard 和持久化验收。
```

避免表述：

```txt
这是完整生产级平台。
所有真实向量检索和权限系统都已经完成。
不需要数据库，只是前端 Demo。
```
