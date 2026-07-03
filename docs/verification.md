# 验收与验证

## 验收目标

本项目当前验收分为五层：

```txt
Docker 基础设施 → uv 后端 → 接口验收 → 构建测试 → 页面验收
```

V2/V3 的主验收路径必须启动 Docker 基础设施。内存 fallback 只用于开发兜底，不能作为主要验收结论。

## 0. 启动 Docker 基础设施

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

检查：

```bash
docker ps
```

需要看到：

```txt
agentflow-postgres
agentflow-redis
agentflow-minio
```

## 1. 启动 uv 后端

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
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

检查：

```bash
curl http://localhost:8000/health
```

## 2. 接口验收

Windows：

```cmd
scripts\verify-local.cmd
```

Linux / macOS / Git Bash：

```bash
bash scripts/verify-local.sh
```

### 当前覆盖项

| 步骤 | 验证内容 | 接口 |
|---|---|---|
| 1 | 后端健康检查 | `GET /health` |
| 2 | 系统模块健康检查 | `GET /api/system/health/full` |
| 3 | Dashboard 聚合 | `GET /api/dashboard/summary` |
| 4 | 知识库列表 | `GET /api/knowledge-bases` |
| 5 | 知识库 RAG 问答 | `POST /api/knowledge-bases/1/query` |
| 6 | 工具列表 | `GET /api/tools` |
| 7 | Agent 工具调用与 trace | `POST /api/agents/1/chat` |
| 8 | 工具审计统计 | `GET /api/audit/tools/summary` |
| 9 | 工具审计记录 | `GET /api/audit/tools` |
| 10 | Prompt 列表 | `GET /api/prompts` |
| 11 | Workflow 运行 | `POST /api/workflows/1/run` |
| 12 | Eval 评测运行 | `POST /api/evals/runs` |

## 3. 后端测试

```bash
cd apps/api
uv run python -m compileall app
uv run python -m pytest
```

根目录脚本：

```bash
pnpm test:api
```

## 4. 前端构建

```bash
pnpm --filter @agentflow/web build
```

或：

```bash
pnpm build:web
```

用于验证：

- Next.js 是否能生产构建。
- TypeScript 是否通过。
- 页面和组件 import 是否正常。

## 5. 页面验收

| 页面 | 验收点 |
|---|---|
| `/demo` | 可看到 V3 在线演示动线 |
| `/showcase` | 可看到作品展示入口 |
| `/dashboard` | 可看到调用量、Token、耗时、失败率等看板信息 |
| `/settings` | 可新增供应商，供应商固定格式字段为下拉选项，API Key 脱敏回显 |
| `/chat` | 可发送问题并收到后端回答 |
| `/knowledge` | 可上传 txt/md/pdf，问答返回引用来源 |
| `/agents` | 可看到 Agent 调用工具链路、trace_id、audit_id |
| `/workflows` | 可运行 V3 可视化工作流画布 |
| `/audit` | 可查看工具调用审计记录与详情 |
| `/prompts` | 可测试 Prompt 变量渲染 |
| `/evals` | 可运行 Prompt/Eval 对比 |
| `/verification` | 页面内系统体检通过 |

## 6. 完整 Docker 模式

完整 Docker 模式不是你当前推荐开发方式，但仍保留用于部署演示：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

注意：当前 `.env.example` 默认适配本地 uv 后端。如果要完整 Docker 跑 api，`DATABASE_URL`、`REDIS_URL`、`MINIO_ENDPOINT` 需要改为 Docker service name，例如 `postgres`、`redis`、`minio`。

## 7. 常见判断

### 接口返回 fallback 或 strategy=local_vector

说明数据库不可用或相关表未初始化。先启动基础设施：

```bash
scripts\dev-infra.cmd
```

再重启 uv 后端。

### Health 通过，但 Settings 保存失败

大概率是数据库未启动或 `.env` 仍使用 Docker 内部主机名。uv 本地后端需要：

```txt
DATABASE_URL=postgresql+psycopg://agentflow:agentflow@localhost:5432/agentflow
REDIS_URL=redis://localhost:6379/0
MINIO_ENDPOINT=localhost:9000
```

### 接口全部 PASS，但页面空白

优先检查前端环境：

```bash
pnpm install
pnpm dev:web
```
