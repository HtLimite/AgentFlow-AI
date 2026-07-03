# 本地开发与启动

## 推荐本地架构

Windows 本地推荐：

```txt
前端 Next.js：本地 pnpm 启动
后端 FastAPI：本地 uvicorn 启动
PostgreSQL / Redis / MinIO：Docker 启动
```

这样既保留完整功能需要的基础设施，又方便前后端热更新调试。

## 1. 准备环境

需要：

- Node.js 20+
- pnpm 9+
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

## 2. 启动基础设施

完整功能建议启动 postgres、redis、minio：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
```

查看容器：

```bash
docker ps
```

停止基础设施：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env down
```

完整 Docker 启动，包括 web/api/nginx：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d --build
```

## 3. 启动后端

```bash
cd apps/api
python -m venv .venv
.venv\Scripts\activate
pip install -e .
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
| Showcase | `/showcase` | 作品展示入口 |
| Dashboard | `/dashboard` | 看板与观测数据 |
| Settings | `/settings` | 模型供应商配置 |
| Chat | `/chat` | Chat Playground |
| Knowledge | `/knowledge` | 文档上传、RAG 问答 |
| Agents | `/agents` | Agent 工具调用 |
| Workflows | `/workflows` | 工作流执行链路 |
| Prompts | `/prompts` | Prompt 模板与变量 |
| Evals | `/evals` | 评测运行 |
| Verification | `/verification` | 页面内验收中心 |

## 6. Windows 常见问题

### verify-local.cmd 中文乱码

现在脚本只输出 ASCII 验收摘要，避免 Windows 终端中文编码问题。拉取最新代码后执行：

```cmd
scripts\verify-local.cmd
```

### 后端连接数据库失败

先确认 Docker Desktop 已启动，再执行：

```bash
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio
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

## 7. 本地开发最小闭环

```bash
# 1. 基础设施
docker compose -f deploy/docker-compose.yml --env-file .env up -d postgres redis minio

# 2. 后端
cd apps/api
.venv\Scripts\activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 3. 前端
pnpm dev:web

# 4. 验收
scripts\verify-local.cmd
```
