# 本地开发与启动

## 推荐本地架构

Windows 本地推荐：

```txt
前端 Next.js：本地 pnpm 启动
后端 FastAPI：本地 uv 启动
PostgreSQL / Redis / MinIO：Docker 启动
```

这不是“只跑 demo 内存效果”。V4 的主路径需要 Docker 基础设施提供数据库、缓存和对象存储；内存 fallback 只作为数据库不可用时的兜底。

## 1. 准备环境

需要：

- Node.js 20+
- pnpm 9+
- uv
- Python 3.12+
- Docker Desktop

首次进入项目：

```bash
git clone git@github.com:HtLimite/AgentFlow-AI.git
cd AgentFlow-AI
cp .env.example .env
pnpm install
```

Windows PowerShell 没有 `cp` 时可用：

```powershell
Copy-Item .env.example .env
```

当前 `.env.example` 默认适配本地 uv 后端，关键地址应该是：

```txt
DATABASE_URL=postgresql+psycopg://agentflow:agentflow@localhost:5432/agentflow
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=localhost:9000
```

## 2. 启动 Docker 基础设施

Windows：

```cmd
scripts\dev-infra.cmd
```

Linux / macOS / Git Bash：

```bash
bash scripts/dev-infra.sh
```

等价命令：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
```

查看容器：

```bash
docker ps
```

需要看到：

```txt
agentflow-postgres
agentflow-redis
agentflow-minio
```

停止基础设施：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env down
```

## 3. 启动 uv 后端

Windows：

```cmd
scripts\dev-api-uv.cmd
```

Linux / macOS / Git Bash：

```bash
bash scripts/dev-api-uv.sh
```

等价命令：

```bash
cd apps/api
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

后端地址：

```txt
http://localhost:8000
http://localhost:8000/health
http://localhost:8000/docs
```

## 4. 启动前端

项目根目录：

```bash
pnpm dev:web
```

前端地址：

```txt
http://localhost:3000
```

## 5. 常用页面

| 页面 | 地址 | 作用 |
|---|---|---|
| Demo | `/demo` | V4 演示动线 |
| Showcase | `/showcase` | 作品展示入口 |
| Dashboard | `/dashboard` | 看板与观测数据 |
| Settings | `/settings` | 模型供应商配置 |
| Chat | `/chat` | Chat Playground |
| Knowledge | `/knowledge` | 文档上传、RAG 问答 |
| Agents | `/agents` | Agent 工具调用与 trace |
| Workflows | `/workflows` | React Flow 工作流画布 |
| Audit | `/audit` | 工具调用审计 |
| Prompts | `/prompts` | Prompt 模板与变量 |
| Evals | `/evals` | Prompt/Eval 对比 |
| Verification | `/verification` | 页面内验收中心 |

## 6. 验收

Windows：

```cmd
scripts\verify-local.cmd
```

Linux / macOS / Git Bash：

```bash
bash scripts/verify-local.sh
```

构建与测试：

```bash
pnpm --filter @agentflow/web build
cd apps/api
uv run python -m compileall app
uv run python -m pytest
```

## 7. 完整 Docker 模式

完整 Docker 模式仍然保留，但不是当前推荐开发方式：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

如果完整 Docker 跑 api，需要把 `.env` 中的服务地址改成 Docker service name：

```txt
DATABASE_URL=postgresql+psycopg://agentflow:agentflow@postgres:5432/agentflow
REDIS_URL=redis://redis:6379/0
MINIO_ENDPOINT=minio:9000
```

## 8. Windows 常见问题

### 后端连接数据库失败

先确认 Docker Desktop 已启动，再执行：

```cmd
scripts\dev-infra.cmd
```

然后重启 uv 后端。

### 使用 uv 后端却连接 postgres 失败

检查 `.env` 是否仍写着 `@postgres:5432`。本地 uv 后端必须使用 `@localhost:5432`。

### 接口返回 fallback 或 strategy=local_vector

说明数据库不可用或表未初始化。重新启动基础设施并重启后端：

```cmd
scripts\dev-infra.cmd
scripts\dev-api-uv.cmd
```

### 端口冲突

常用端口：

```txt
3000：前端
8000：后端
5432：PostgreSQL
6379：Redis
9000 / 9001：MinIO
8080：Docker nginx
```

如果端口被占用，优先停掉旧进程或旧容器。

## 9. 本地开发完整闭环

```cmd
scripts\dev-infra.cmd
scripts\dev-api-uv.cmd
pnpm dev:web
scripts\verify-local.cmd
```
